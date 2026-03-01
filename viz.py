import matplotlib.pyplot as plt

def plot_explanation(keyword_importances):
    """
    Takes the output from LIME and makes a bar chart.
    keyword_importances example: [('apr', 0.9), ('notice', 0.4)]
    """
    # Sort for better visuals
    keyword_importances.sort(key=lambda x: x[1])
    
    words = [x[0] for x in keyword_importances]
    scores = [x[1] for x in keyword_importances]
    
    plt.figure(figsize=(10, 6))
    colors = ['red' if s > 0.5 else 'orange' for s in scores]
    plt.barh(words, scores, color=colors)
    plt.xlim(0, 1)
    plt.title("XAI Risk Contribution Scores")
    plt.xlabel("Influence on Risk Label (0 to 1)")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()