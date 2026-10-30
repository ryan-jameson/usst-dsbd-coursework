import numpy as np
from collections import defaultdict

class TemporalFeatureExtractor:
    def __init__(self, field_width=105, field_height=68):
        self.field_width = field_width
        self.field_height = field_height
        self.track_history = defaultdict(list)
    
    def extract_player_features(self, tracks):
        features = []
        
        for track_id, track in tracks.items():
            bbox = track['bbox']
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            velocity = track.get('velocity', np.array([0, 0]))
            speed = np.linalg.norm(velocity)
            
            direction = np.arctan2(velocity[1], velocity[0]) if speed > 0 else 0
            
            feature = {
                'track_id': track_id,
                'class': track['class'],
                'position': [center_x, center_y],
                'speed': float(speed),
                'direction': float(direction),
                'bbox': bbox
            }
            
            features.append(feature)
        
        return features

    def _smoothed_speed(self, track_id, window=3):
        """Return smoothed speed from track history (most recent N entries)."""
        hist = self.track_history.get(track_id, [])
        if not hist:
            return 0.0
        speeds = [h.get('speed', 0.0) for h in hist[-window:]]
        return float(np.mean(speeds))
    
    def extract_team_features(self, player_features):
        home_players = [p for p in player_features if p['class'] == 'home_player']
        away_players = [p for p in player_features if p['class'] == 'away_player']
        
        home_center = self._compute_center(home_players) if home_players else [0, 0]
        away_center = self._compute_center(away_players) if away_players else [0, 0]
        
        home_avg_speed = np.mean([p['speed'] for p in home_players]) if home_players else 0
        away_avg_speed = np.mean([p['speed'] for p in away_players]) if away_players else 0
        
        return {
            'home_count': len(home_players),
            'away_count': len(away_players),
            'home_center': home_center,
            'away_center': away_center,
            'home_avg_speed': home_avg_speed,
            'away_avg_speed': away_avg_speed,
            'distance_between_centers': np.linalg.norm(np.array(home_center) - np.array(away_center))
        }
    
    def _compute_center(self, players):
        x_coords = [p['position'][0] for p in players]
        y_coords = [p['position'][1] for p in players]
        return [np.mean(x_coords), np.mean(y_coords)]
    
    def extract_possession_feature(self, player_features, ball_bbox):
        if ball_bbox is None:
            return {'possession_team': None, 'possession_player_id': None}
        
        ball_center = [(ball_bbox[0] + ball_bbox[2]) // 2, (ball_bbox[1] + ball_bbox[3]) // 2]
        
        min_distance = float('inf')
        closest_player = None
        
        for player in player_features:
            player_center = player['position']
            distance = np.linalg.norm(np.array(ball_center) - np.array(player_center))
            
            if distance < min_distance:
                min_distance = distance
                closest_player = player
        
        if closest_player and min_distance < 50:
            possession_team = 'home' if closest_player['class'] == 'home_player' else 'away'
            return {
                'possession_team': possession_team,
                'possession_player_id': closest_player['track_id'],
                'distance_to_ball': min_distance
            }
        
        return {'possession_team': None, 'possession_player_id': None}
    
    def extract_spatial_features(self, player_features):
        if not player_features:
            return {}
        
        all_positions = np.array([p['position'] for p in player_features])
        
        x_mean = np.mean(all_positions[:, 0])
        y_mean = np.mean(all_positions[:, 1])
        x_std = np.std(all_positions[:, 0])
        y_std = np.std(all_positions[:, 1])
        
        return {
            'mean_position': [x_mean, y_mean],
            'std_position': [x_std, y_std],
            'spread': np.sqrt(x_std**2 + y_std**2)
        }
    
    def extract_frame_features(self, tracks):
        player_features = self.extract_player_features(tracks)
        
        ball_bbox = None
        for track_id, track in tracks.items():
            if track['class'] == 'ball':
                ball_bbox = track['bbox']
                break
        
        team_features = self.extract_team_features(player_features)
        possession_features = self.extract_possession_feature(player_features, ball_bbox)
        spatial_features = self.extract_spatial_features(player_features)
        
        frame_features = {
            'num_players': len(player_features),
            'team_features': team_features,
            'possession_features': possession_features,
            'spatial_features': spatial_features,
            'ball_detected': ball_bbox is not None
        }
        
        for track_id, track in tracks.items():
            self.track_history[track_id].append({
                'position': [(track['bbox'][0]+track['bbox'][2])//2, (track['bbox'][1]+track['bbox'][3])//2],
                'speed': float(np.linalg.norm(track.get('velocity', [0, 0])))
            })
        
        return frame_features

    def frame_to_node_features(self, tracks, image_shape, max_nodes=23):
        """
        将一帧的跟踪结果转换为固定长度的节点特征列表，适配分类器输入格式。
        返回 shape: (max_nodes, 6) 的 list，每个节点为 [x_m, y_m, speed, direction, team_flag, extra]
        image_shape: (height, width, channels)
        """
        h, w = image_shape[0], image_shape[1]
        nodes = []

        # Ensure consistent ordering: sort by class (ball last) then track_id
        def sort_key(item):
            tid, tr = item
            cls = tr.get('class', '')
            # put ball at end
            cls_priority = 2 if cls == 'ball' else (0 if cls == 'home_player' else 1)
            return (cls_priority, tid)

        for track_id, track in sorted(tracks.items(), key=sort_key):
            bbox = track['bbox']
            center_x = (bbox[0] + bbox[2]) / 2.0
            center_y = (bbox[1] + bbox[3]) / 2.0

            # map pixels -> meters (field_width x field_height)
            x_m = (center_x / float(w)) * self.field_width
            y_m = (center_y / float(h)) * self.field_height

            velocity = np.array(track.get('velocity', [0.0, 0.0]), dtype=float)
            # use smoothed speed when available
            raw_speed = float(np.linalg.norm(velocity))
            speed = self._smoothed_speed(track_id) if track_id in self.track_history else raw_speed
            direction = float(np.arctan2(velocity[1], velocity[0])) if speed > 0 else 0.0

            # team flag: home=1, away=0, ball=0.5
            clsname = track.get('class', '')
            if clsname == 'home_player':
                team_flag = 1.0
            elif clsname == 'away_player':
                team_flag = 0.0
            elif clsname == 'ball':
                team_flag = 0.5
            else:
                team_flag = 0.0

            node = [x_m, y_m, speed, direction, team_flag, 0.0]
            nodes.append(node)

        # pad or truncate to max_nodes
        if len(nodes) >= max_nodes:
            nodes = nodes[:max_nodes]
        else:
            for _ in range(max_nodes - len(nodes)):
                nodes.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        return nodes

    def build_sequence_for_classifier(self, frame_nodes_list, num_frames=16):
        """
        将若干帧的节点特征列表构造成分类器需要的序列输入格式：
        返回 shape: (num_frames, max_nodes, 6)
        如果帧数不足则在前面填充零帧，超过则取最近 num_frames 帧。
        """
        if not frame_nodes_list:
            # return zero sequence
            return np.zeros((num_frames, 23, 6), dtype=float)

        max_nodes = len(frame_nodes_list[0])
        if len(frame_nodes_list) >= num_frames:
            seq = frame_nodes_list[-num_frames:]
        else:
            pad_count = num_frames - len(frame_nodes_list)
            pad = [[[0.0]*6 for _ in range(max_nodes)] for _ in range(pad_count)]
            seq = pad + frame_nodes_list

        # return numpy array with shape (num_frames, max_nodes, 6)
        return np.array(seq, dtype=float)
    
    def extract_sequence_features(self, frame_features_list):
        if len(frame_features_list) < 2:
            return {}
        
        possession_sequence = [f['possession_features']['possession_team'] for f in frame_features_list]
        
        possession_changes = 0
        for i in range(1, len(possession_sequence)):
            if possession_sequence[i] != possession_sequence[i-1]:
                possession_changes += 1
        
        avg_speed_sequence = []
        for f in frame_features_list:
            home_speed = f['team_features']['home_avg_speed']
            away_speed = f['team_features']['away_avg_speed']
            avg_speed_sequence.append((home_speed + away_speed) / 2)
        
        return {
            'possession_changes': possession_changes,
            'avg_speed': np.mean(avg_speed_sequence),
            'speed_variance': np.var(avg_speed_sequence),
            'avg_spread': np.mean([f['spatial_features']['spread'] for f in frame_features_list])
        }

def main():
    from collections import deque
    import os
    
    extractor = TemporalFeatureExtractor()
    
    mock_tracks = {
        0: {'bbox': [100, 200, 150, 300], 'class': 'home_player', 'velocity': [2, 1]},
        1: {'bbox': [200, 250, 250, 350], 'class': 'away_player', 'velocity': [-1, 0]},
        2: {'bbox': [500, 400, 510, 410], 'class': 'ball', 'velocity': [5, 2]}
    }
    
    frame_features = extractor.extract_frame_features(mock_tracks)
    print("Frame Features:")
    print(json.dumps(frame_features, indent=2, default=str))
    
    sequence_features = extractor.extract_sequence_features([frame_features] * 16)
    print("\nSequence Features:")
    print(json.dumps(sequence_features, indent=2, default=str))

if __name__ == '__main__':
    import json
    main()