from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, roc_curve
import matplotlib.pyplot as plt
import pandas as pd

def plot_metrics(y_true, y_scores, title):
    # ROC
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = roc_auc_score(y_true, y_scores)
    
    # PRC
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    prc_auc = auc(recall, precision)
    
    # Graficar
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.4f}')
    plt.title(f'ROC Curve - {title}')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(recall, precision, label=f'AUC = {prc_auc:.4f}')
    plt.title(f'PRC Curve - {title}')
    plt.legend()
    
    plt.show()
    print(f"{title} -> ROC-AUC: {roc_auc:.4f}, PRC-AUC: {prc_auc:.4f}")

# Cargar etiquetas y scores de MIDAS
y_true = pd.read_csv('user1_labels.csv', header=None)
y_scores = pd.read_csv('scores_user1.txt', header=None)
plot_metrics(y_true, y_scores, "User 1 (MIDAS)")