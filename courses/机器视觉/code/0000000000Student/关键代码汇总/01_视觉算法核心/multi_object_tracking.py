import cv2
import numpy as np
from collections import deque
import os
from scipy.optimize import linear_sum_assignment

class FootballTracker:
    def __init__(self, max_history=10, max_age=5, iou_threshold=0.3):
        self.tracks = {}
        self.next_id = 0
        self.max_history = max_history
        self.max_age = max_age
        self.iou_threshold = iou_threshold
    
    def _compute_iou(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _hungarian_match(self, iou_matrix):
        row_ind, col_ind = linear_sum_assignment(-iou_matrix)
        matches = []
        for r, c in zip(row_ind, col_ind):
            if iou_matrix[r, c] > self.iou_threshold:
                matches.append((r, c))
        return matches
    
    def _predict_position(self, track):
        if len(track['history']) < 2:
            return track['bbox']
        
        recent_history = list(track['history'])[-5:]
        velocities = []
        
        for i in range(1, len(recent_history)):
            prev = recent_history[i-1]
            curr = recent_history[i]
            vx = (curr[0] + curr[2])//2 - (prev[0] + prev[2])//2
            vy = (curr[1] + curr[3])//2 - (prev[1] + prev[3])//2
            velocities.append((vx, vy))
        
        if velocities:
            avg_vx = sum(v[0] for v in velocities) / len(velocities)
            avg_vy = sum(v[1] for v in velocities) / len(velocities)
            
            curr_bbox = track['bbox']
            curr_center = [(curr_bbox[0]+curr_bbox[2])//2, (curr_bbox[1]+curr_bbox[3])//2]
            new_center = [int(curr_center[0] + avg_vx), int(curr_center[1] + avg_vy)]
            
            width = curr_bbox[2] - curr_bbox[0]
            height = curr_bbox[3] - curr_bbox[1]
            
            return [
                new_center[0] - width//2,
                new_center[1] - height//2,
                new_center[0] + width//2,
                new_center[1] + height//2
            ]
        
        return track['bbox']
    
    def update(self, detections):
        updated_tracks = {}
        
        if not self.tracks:
            for det in detections:
                self.tracks[self.next_id] = {
                    'id': self.next_id,
                    'bbox': det['bbox'],
                    'class': det['class'],
                    'history': deque([det['bbox']], maxlen=self.max_history),
                    'velocity': np.array([0, 0]),
                    'age': 0
                }
                self.next_id += 1
            return self.tracks
        
        track_ids = list(self.tracks.keys())
        predicted_bboxes = np.array([self._predict_position(self.tracks[t]) for t in track_ids])
        det_bboxes = np.array([d['bbox'] for d in detections])
        
        iou_matrix = np.zeros((len(track_ids), len(detections)))
        for i, track_bbox in enumerate(predicted_bboxes):
            for j, det_bbox in enumerate(det_bboxes):
                iou_matrix[i, j] = self._compute_iou(track_bbox, det_bbox)
        
        matched_indices = self._hungarian_match(iou_matrix)
        
        for track_idx, det_idx in matched_indices:
            track_id = track_ids[track_idx]
            det = detections[det_idx]
            
            prev_center = np.array([
                (self.tracks[track_id]['bbox'][0] + self.tracks[track_id]['bbox'][2]) // 2,
                (self.tracks[track_id]['bbox'][1] + self.tracks[track_id]['bbox'][3]) // 2
            ])
            curr_center = np.array([(det['bbox'][0] + det['bbox'][2]) // 2, (det['bbox'][1] + det['bbox'][3]) // 2])
            
            velocity = curr_center - prev_center
            
            self.tracks[track_id]['bbox'] = det['bbox']
            self.tracks[track_id]['class'] = det['class']
            self.tracks[track_id]['history'].append(det['bbox'])
            self.tracks[track_id]['velocity'] = velocity
            self.tracks[track_id]['age'] = 0
            updated_tracks[track_id] = self.tracks[track_id]
        
        unmatched_track_ids = set(track_ids) - set([track_ids[i] for i, _ in matched_indices])
        for track_id in unmatched_track_ids:
            self.tracks[track_id]['age'] += 1
            if self.tracks[track_id]['age'] <= self.max_age:
                predicted = self._predict_position(self.tracks[track_id])
                self.tracks[track_id]['bbox'] = predicted
                self.tracks[track_id]['history'].append(predicted)
                updated_tracks[track_id] = self.tracks[track_id]
        
        unmatched_dets = set(range(len(detections))) - set([d for _, d in matched_indices])
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            self.tracks[self.next_id] = {
                'id': self.next_id,
                'bbox': det['bbox'],
                'class': det['class'],
                'history': deque([det['bbox']], maxlen=self.max_history),
                'velocity': np.array([0, 0]),
                'age': 0
            }
            updated_tracks[self.next_id] = self.tracks[self.next_id]
            self.next_id += 1
        
        self.tracks = updated_tracks
        return self.tracks
    
    def draw_tracks(self, image, tracks):
        for track_id, track in tracks.items():
            x1, y1, x2, y2 = track['bbox']
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f'ID:{track_id}', (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            history = list(track['history'])
            if len(history) > 1:
                for i in range(len(history)-1):
                    prev_bbox = history[i]
                    curr_bbox = history[i+1]
                    prev_center = ((prev_bbox[0]+prev_bbox[2])//2, (prev_bbox[1]+prev_bbox[3])//2)
                    curr_center = ((curr_bbox[0]+curr_bbox[2])//2, (curr_bbox[1]+curr_bbox[3])//2)
                    cv2.line(image, prev_center, curr_center, (0, 255, 0), 1)
        
        return image

def main():
    from object_detection import FootballDetector
    
    detector = FootballDetector()
    tracker = FootballTracker()
    
    input_dir = r'../Soccer/S_BHA vs MU'
    output_dir = r'../outputs/tracking'
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in sorted(os.listdir(input_dir))[:20]:
        if not filename.endswith('.jpg'):
            continue
        
        img_path = os.path.join(input_dir, filename)
        image = cv2.imread(img_path)
        
        if image is None:
            continue
        
        detections = detector.detect(image)
        tracks = tracker.update(detections)
        image = tracker.draw_tracks(image, tracks)
        
        output_path = os.path.join(output_dir, f'track_{filename}')
        cv2.imwrite(output_path, image)
        
        print(f"Processed {filename}: {len(tracks)} active tracks")

if __name__ == '__main__':
    main()