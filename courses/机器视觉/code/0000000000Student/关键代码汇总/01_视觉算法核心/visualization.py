import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class FootballVisualizer:
    def __init__(self):
        self.colors = {
            'home_player': (0, 0, 255),
            'away_player': (255, 0, 0),
            'goalkeeper': (0, 255, 255),
            'referee': (0, 128, 128),
            'ball': (255, 255, 0),
            'field_point': (255, 0, 255)
        }
        
        self.tactical_colors = {
            '阵地进攻': (0, 255, 0),
            '快速反击': (255, 255, 0),
            '边路进攻': (0, 255, 255),
            '中路渗透': (128, 0, 255),
            '阵地防守': (255, 0, 0),
            '收缩防守': (255, 128, 0),
            '高位逼抢': (0, 128, 255),
            '定位球': (128, 128, 128),
            '死球': (64, 64, 64)
        }
    
    def draw_detections(self, image, detections):
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = self.colors.get(det['class'], (255, 0, 255))
            
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det['class']}: {det['confidence']:.2f}"
            cv2.putText(image, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def draw_tracks(self, image, tracks):
        for track_id, track in tracks.items():
            x1, y1, x2, y2 = track['bbox']
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f'ID:{track_id}', (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            history = list(track.get('history', []))
            if len(history) > 1:
                for i in range(len(history)-1):
                    prev_bbox = history[i]
                    curr_bbox = history[i+1]
                    prev_center = ((prev_bbox[0]+prev_bbox[2])//2, (prev_bbox[1]+prev_bbox[3])//2)
                    curr_center = ((curr_bbox[0]+curr_bbox[2])//2, (curr_bbox[1]+curr_bbox[3])//2)
                    cv2.line(image, prev_center, curr_center, (0, 255, 0), 1)
        
        return image
    
    def draw_tactical_info(self, image, tactical_state):
        cv2.putText(image, f'Tactical: {tactical_state}', (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return image
    
    def draw_offside_line(self, image, offside_y):
        height = image.shape[0]
        cv2.line(image, (0, offside_y), (image.shape[1], offside_y), 
                 (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(image, 'Offside Line', (20, offside_y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return image
    
    def draw_field_overlay(self, image):
        height, width = image.shape[:2]
        
        field_width_px = width
        field_height_px = int(width * 68 / 105)
        
        start_y = (height - field_height_px) // 2
        
        cv2.rectangle(image, (0, start_y), (width, start_y + field_height_px),
                      (0, 128, 0), 1)
        
        midline_y = start_y + field_height_px // 2
        cv2.line(image, (width//2, start_y), (width//2, start_y + field_height_px),
                 (255, 255, 255), 1)
        
        cv2.circle(image, (width//2, midline_y), int(min(width, field_height_px)*0.08),
                   (255, 255, 255), 1)
        
        return image
    
    def generate_heatmap(self, positions, output_path='heatmap.png', 
                         field_width=105, field_height=68):
        heatmap = np.zeros((int(field_height), int(field_width)))
        
        for pos in positions:
            x, y = pos
            if 0 <= x < field_width and 0 <= y < field_height:
                heatmap[int(y), int(x)] += 1
        
        plt.figure(figsize=(10.5, 6.8))
        plt.imshow(heatmap, cmap='hot', interpolation='nearest')
        plt.colorbar(label='停留次数')
        plt.title('球员跑动热力图')
        plt.xlabel('场地长度 (m)')
        plt.ylabel('场地宽度 (m)')
        
        plt.plot([0, field_width], [field_height/2 - 9.15, field_height/2 - 9.15], 'w--')
        plt.plot([0, field_width], [field_height/2 + 9.15, field_height/2 + 9.15], 'w--')
        
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"Heatmap saved to {output_path}")
    
    def generate_possession_chart(self, home_possession, away_possession, output_path='possession.png'):
        labels = ['主队控球', '客队控球']
        sizes = [home_possession, away_possession]
        colors = ['#FF0000', '#0000FF']
        
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 12})
        plt.axis('equal')
        plt.title('控球率统计')
        
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"Possession chart saved to {output_path}")
    
    def save_visualized_frame(self, image, detections=None, tracks=None, 
                              tactical_state=None, output_path='output.jpg'):
        if detections:
            image = self.draw_detections(image, detections)
        if tracks:
            image = self.draw_tracks(image, tracks)
        if tactical_state:
            image = self.draw_tactical_info(image, tactical_state)
        
        cv2.imwrite(output_path, image)
        print(f"Visualized frame saved to {output_path}")

def main():
    visualizer = FootballVisualizer()
    
    input_path = r'../Soccer/S_BHA vs MU/000001.jpg'
    image = cv2.imread(input_path)
    
    if image is not None:
        detections = [
            {'bbox': [100, 200, 150, 300], 'class': 'home_player', 'confidence': 0.95},
            {'bbox': [200, 250, 250, 350], 'class': 'away_player', 'confidence': 0.92},
            {'bbox': [500, 400, 510, 410], 'class': 'ball', 'confidence': 0.88}
        ]
        
        tracks = {
            0: {'bbox': [100, 200, 150, 300], 'history': [[100, 200, 150, 300], [105, 205, 155, 305]]},
            1: {'bbox': [200, 250, 250, 350], 'history': [[200, 250, 250, 350], [195, 245, 245, 345]]}
        }
        
        image = visualizer.draw_detections(image, detections)
        image = visualizer.draw_tracks(image, tracks)
        image = visualizer.draw_tactical_info(image, '进攻状态 - 阵地进攻')
        image = visualizer.draw_field_overlay(image)
        
        output_dir = r'../outputs/visualization'
        os.makedirs(output_dir, exist_ok=True)
        
        cv2.imwrite(os.path.join(output_dir, 'visualized_frame.jpg'), image)
        print("Visualized frame saved!")
        
        positions = np.random.rand(1000, 2) * [105, 68]
        visualizer.generate_heatmap(positions, os.path.join(output_dir, 'heatmap.png'))
        
        visualizer.generate_possession_chart(55.2, 44.8, os.path.join(output_dir, 'possession.png'))

if __name__ == '__main__':
    main()