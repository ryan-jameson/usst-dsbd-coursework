import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import FootballDataPreprocessor
from object_detection import FootballDetector
from multi_object_tracking import FootballTracker
from temporal_feature_extraction import TemporalFeatureExtractor
from tactical_classification import TacticalClassifier, generate_mock_data
from visualization import FootballVisualizer

class FootballAnalysisSystem:
    def __init__(self, use_mock=False):
        # allow forcing mock detector for offline testing
        self.detector = FootballDetector(use_mock=use_mock)
        self.tracker = FootballTracker()
        self.feature_extractor = TemporalFeatureExtractor()
        self.classifier = TacticalClassifier()
        self.visualizer = FootballVisualizer()
        
        self.output_dir = r'../outputs'
        os.makedirs(self.output_dir, exist_ok=True)
        # frame node buffer for sequence-based classification
        self.frame_node_buffer = []
        self.num_seq_frames = 16
    
    def run_detection(self, image):
        return self.detector.detect(image)
    
    def run_tracking(self, detections):
        return self.tracker.update(detections)
    
    def extract_features(self, tracks):
        return self.feature_extractor.extract_frame_features(tracks)
    
    def classify_tactics(self, tracks, image=None, mode='auto'):
        """
        mode: 'auto' | 'rule' | 'sequence'
        - 'rule': 使用单帧规则判断（速度、控球、球员密度）
        - 'sequence': 使用序列化节点特征并调用深度分类器
        - 'auto': 优先sequence（当缓存帧数足够），否则用rule
        """
        # Single-frame rule-based heuristics
        def rule_based(tracks):
            # 简单启发式：若球被检测到并靠近某队且该队多名球员位于对方半场 -> 进攻
            frame_feats = self.feature_extractor.extract_frame_features(tracks)
            poss = frame_feats.get('possession_features', {}).get('possession_team')
            home_center_x = frame_feats['team_features']['home_center'][0]
            away_center_x = frame_feats['team_features']['away_center'][0]
            # 使用场地长度 105m 的中线判断
            mid_x = 105.0 / 2.0
            if poss == 'home' and home_center_x > mid_x:
                return {'tactical_class': '阵地进攻', 'method': 'rule'}
            if poss == 'away' and away_center_x < mid_x:
                return {'tactical_class': '阵地进攻', 'method': 'rule'}

            # 定位球检测：球静止或速度极低且多人聚集
            if frame_feats.get('ball_detected'):
                dist_info = frame_feats.get('possession_features', {})
                if dist_info.get('distance_to_ball') is not None and dist_info.get('distance_to_ball') < 2.0:
                    # further check: players count in small region
                    if frame_feats['team_features']['home_count'] + frame_feats['team_features']['away_count'] > 6:
                        return {'tactical_class': '定位球', 'method': 'rule'}

            # 快速反击启发式：平均速度较高
            seq_stats = self.feature_extractor.extract_sequence_features([frame_feats])
            if seq_stats and seq_stats.get('avg_speed', 0) > 3.0:
                return {'tactical_class': '快速反击', 'method': 'rule'}

            return {'tactical_class': '阵地防守', 'method': 'rule'}

        if mode == 'rule':
            return rule_based(tracks)

        # build node features for this frame and append to buffer
        if image is None:
            img_shape = (720, 1280, 3)
        else:
            img_shape = image.shape

        frame_nodes = self.feature_extractor.frame_to_node_features(tracks, img_shape, max_nodes=23)
        self.frame_node_buffer.append(frame_nodes)
        if len(self.frame_node_buffer) > self.num_seq_frames:
            self.frame_node_buffer = self.frame_node_buffer[-self.num_seq_frames:]

        if mode == 'sequence' or (mode == 'auto' and len(self.frame_node_buffer) >= self.num_seq_frames):
            seq = self.feature_extractor.build_sequence_for_classifier(self.frame_node_buffer, num_frames=self.num_seq_frames)
            pred = self.classifier.predict(seq)
            pred['method'] = 'sequence'
            return pred

        # fallback to rule-based
        return rule_based(tracks)
    
    def visualize(self, image, detections, tracks, tactical_state):
        image = self.visualizer.draw_detections(image, detections)
        image = self.visualizer.draw_tracks(image, tracks)
        image = self.visualizer.draw_tactical_info(image, tactical_state)
        return image
    
    def process_video_sequence(self, input_dir, num_frames=10):
        frame_features_list = []
        
        for idx, filename in enumerate(sorted(os.listdir(input_dir))):
            if idx >= num_frames:
                break
            
            if not filename.endswith('.jpg'):
                continue
            
            img_path = os.path.join(input_dir, filename)
            image = cv2.imread(img_path)
            
            if image is None:
                continue
            
            detections = self.run_detection(image)
            tracks = self.run_tracking(detections)
            frame_features = self.extract_features(tracks)
            frame_features_list.append(frame_features)

            # classify using tracks + image; system will choose sequence if enough frames
            tactical_pred = self.classify_tactics(tracks, image, mode='auto')
            tactical_state = tactical_pred['tactical_class']
            
            image = self.visualize(image, detections, tracks, tactical_state)
            
            output_path = os.path.join(self.output_dir, f'output_{filename}')
            cv2.imwrite(output_path, image)
            
            print(f"Processed frame {idx+1}/{num_frames}: {filename}")
            print(f"  - Detections: {len(detections)}")
            print(f"  - Tracks: {len(tracks)}")
            print(f"  - Tactical State: {tactical_state}")
        
        if frame_features_list:
            sequence_features = self.feature_extractor.extract_sequence_features(frame_features_list)
            print("\nSequence Features:")
            for key, value in sequence_features.items():
                print(f"  {key}: {value}")
        
        print("\nProcessing complete!")

    def process_image_file(self, image_path, save_path=None, mode='auto'):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read image: {image_path}")
            return

        detections = self.run_detection(image)
        tracks = self.run_tracking(detections)

        tactical_pred = self.classify_tactics(tracks, image, mode=mode)
        tactical_state = tactical_pred['tactical_class']

        vis = self.visualize(image.copy(), detections, tracks, tactical_state)

        if save_path is None:
            base = os.path.basename(image_path)
            save_path = os.path.join(self.output_dir, f'vis_{base}')

        cv2.imwrite(save_path, vis)
        print(f"Saved visualization to {save_path} | Tactical: {tactical_state} | Method: {tactical_pred.get('method')}")

    def process_video_file(self, video_path, save_dir=None, max_frames=None, mode='auto'):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video: {video_path}")
            return

        if save_dir is None:
            save_dir = os.path.join(self.output_dir, 'video_frames')
        os.makedirs(save_dir, exist_ok=True)

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.run_detection(frame)
            tracks = self.run_tracking(detections)

            tactical_pred = self.classify_tactics(tracks, frame, mode=mode)
            tactical_state = tactical_pred['tactical_class']

            vis = self.visualize(frame.copy(), detections, tracks, tactical_state)

            out_path = os.path.join(save_dir, f'frame_{frame_idx:06d}.jpg')
            cv2.imwrite(out_path, vis)

            print(f"Frame {frame_idx}: saved {out_path} | Tactical: {tactical_state} | Method: {tactical_pred.get('method')}")

            frame_idx += 1
            if max_frames and frame_idx >= max_frames:
                break

        cap.release()
        print(f"Video processing complete. Frames saved to {save_dir}")
    
    def run_heatmap_analysis(self, positions):
        heatmap_path = os.path.join(self.output_dir, 'heatmap.png')
        self.visualizer.generate_heatmap(positions, heatmap_path)
    
    def run_possession_analysis(self, home_possession, away_possession):
        chart_path = os.path.join(self.output_dir, 'possession.png')
        self.visualizer.generate_possession_chart(home_possession, away_possession)

def main():
    print("=" * 60)
    print("  面向足球赛事理解的机器视觉分析框架")
    print("=" * 60)
    
    system = FootballAnalysisSystem()
    
    print("\n[1] 数据预处理...")
    data_dir = r'../Soccer/S_BHA vs MU'
    preprocessor = FootballDataPreprocessor(data_dir, r'../outputs/dataset')
    preprocessor.process()
    
    print("\n[2] 处理视频序列...")
    system.process_video_sequence(data_dir, num_frames=5)
    
    print("\n[3] 生成分析图表...")
    positions = np.random.rand(1000, 2) * [105, 68]
    system.run_heatmap_analysis(positions)
    system.run_possession_analysis(55.2, 44.8)
    
    print("\n" + "=" * 60)
    print("  分析完成！结果保存在 outputs/ 目录")
    print("=" * 60)

if __name__ == '__main__':
    main()