import numpy as np

class SplitFinder:
    @staticmethod
    def find_split_positions(img_array: np.ndarray, num_splits: int) -> list:
        """
        Find optimal split positions based on white space in the image content.
        
        Args:
            img_array: Image data as numpy array
            num_splits: Number of parts to split into (2 or 3)
        
        Returns:
            List of split positions
            
        Raises:
            ValueError: If num_splits is not 2 or 3
        """
        if num_splits not in [2, 3]:
            raise ValueError("Number of splits must be 2 or 3")
            
        if img_array.size == 0:
            raise ValueError("Empty image array provided")

        # Calculate average brightness per column
        col_brightness = np.mean(img_array, axis=0)
        
        # Smooth brightness values with sliding window
        window_size = 5
        smoothed_brightness = np.convolve(
            col_brightness, 
            np.ones(window_size)/window_size, 
            mode='valid'
        )
        
        # Calculate ideal split intervals
        width = len(smoothed_brightness)
        segment_width = width // num_splits
        
        # Find split positions
        split_positions = []
        for i in range(1, num_splits):
            target_position = i * segment_width
            search_range = int(segment_width * 0.1)  # Search range is 10% of segment width
            start = max(target_position - search_range, 0)
            end = min(target_position + search_range, width)
            
            # Find brightest column in search range
            search_region = smoothed_brightness[start:end]
            max_brightness_idx = np.argmax(search_region)
            split_position = start + max_brightness_idx
            
            split_positions.append(split_position)
        
        return split_positions
