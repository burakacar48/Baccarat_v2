"""
Win/Loss pattern prediction module.
This module analyzes past win/loss patterns to predict future outcomes.
"""
from collections import Counter

class WLPredictionModel:
    """Predicts win/loss patterns based on historical data."""
    
    def __init__(self, lookback_pairs=5):
        """
        Args:
            lookback_pairs (int): Number of win/loss pairs to look back for pattern matching.
        """
        self.lookback_pairs = lookback_pairs
        
    def predict(self, wl_history):
        """
        Analyzes the win/loss history to predict the next outcome based on pair patterns.
        
        Args:
            wl_history (list): List of 'W' and 'L' values representing win/loss history.
            
        Returns:
            str: Predicted value ('W', 'L' or '?').
        """
        if len(wl_history) < 2:
            return '?'
        
        # Extract pairs from history
        pairs = []
        for i in range(0, len(wl_history) - 1, 2):
            if i + 1 < len(wl_history):
                pairs.append(wl_history[i] + wl_history[i + 1])
        
        # If we don't have enough pairs, return unknown
        if len(pairs) < 2:  # Need at least two pairs to find patterns
            return '?'
        
        # Get the most recent pairs up to lookback limit
        recent_pairs = pairs[-min(self.lookback_pairs, len(pairs)):]
        
        # Count occurrences of each pattern
        patterns = Counter()
        for i in range(len(recent_pairs) - 1):
            current_pair = recent_pairs[i]
            next_result = recent_pairs[i + 1][0]  # First element of next pair
            patterns[current_pair + next_result] += 1
        
        # Get the last pair to use for prediction
        last_pair = recent_pairs[-1]
        
        # Find the most common next result after this pair
        best_prediction = '?'
        highest_count = 0
        
        for pattern, count in patterns.items():
            if pattern.startswith(last_pair) and count > highest_count:
                highest_count = count
                if len(pattern) > 2:  # Make sure we have a third character
                    best_prediction = pattern[2]  # The third character is the prediction
        
        # If we didn't find a pattern or only saw it once, use a simple strategy
        if best_prediction == '?' or highest_count <= 1:
            # Predict the opposite of the last result in the pair
            if len(last_pair) > 1:
                return 'W' if last_pair[-1] == 'L' else 'L'
            elif len(wl_history) > 0:
                return 'W' if wl_history[-1] == 'L' else 'L'
        
        return best_prediction
    
    def predict_from_incomplete(self, wl_history):
        """
        Predicts whether the current hand will be a win or loss when we have 
        an incomplete pair (i.e., an odd number of entries in history).
        
        Args:
            wl_history (list): List of 'W' and 'L' values representing win/loss history.
            
        Returns:
            str: Predicted value ('W', 'L' or '?').
        """
        if len(wl_history) < 3:  # Need at least one complete pair + current result
            return '?'
        
        # If we have an odd number of entries, we want to predict the completion of the current pair
        current_result = wl_history[-1]
        
        # Simple strategy: alternate patterns
        # If the last result was a win, predict a loss and vice versa
        predicted_result = 'W' if current_result == 'L' else 'L'
        
        # Check if we have enough history to do more sophisticated prediction
        if len(wl_history) >= 5:  # We need at least 2 complete pairs + current result
            # Extract full pairs from history (ignoring the last incomplete entry)
            pairs = []
            for i in range(0, len(wl_history) - 1, 2):
                if i + 1 < len(wl_history):
                    pairs.append(wl_history[i] + wl_history[i + 1])
            
            # If we have at least 2 complete pairs
            if len(pairs) >= 2:
                # Check if the last two pairs show a pattern
                # Example: if WL -> WL, then predict based on this pattern
                if pairs[-1] == pairs[-2]:
                    # Same pattern repeating, predict the same outcome as before
                    return pairs[-1][1]  # Second char of the last complete pair
                
                # Look for alternating wins and losses
                last_pair_second = pairs[-1][1]  # Second char of last pair
                if last_pair_second == 'W':
                    return 'L'  # After a win, predict a loss
                else:
                    return 'W'  # After a loss, predict a win
        
        # Default to the simple strategy
        return predicted_result
    
    def should_reverse_bet(self, wl_history, main_prediction):
        """
        Determines whether to bet against the main prediction.
        
        Args:
            wl_history (list): List of 'W' and 'L' values representing win/loss history.
            main_prediction (str): Main prediction ('P' or 'B').
            
        Returns:
            tuple: (should_reverse, predicted_wl) - Whether to reverse and the WL prediction.
        """
        # Handle empty history case
        if not wl_history:
            return False, '?'
            
        if len(wl_history) % 2 == 0:  # Even number, predict next pair's first element
            predicted_wl = self.predict(wl_history)
        else:  # Odd number, predict current pair's second element
            predicted_wl = self.predict_from_incomplete(wl_history)
        
        # If prediction is loss or unknown, reverse the bet
        should_reverse = predicted_wl == 'L'
        
        return should_reverse, predicted_wl