import numpy as np
import matplotlib.pyplot as plt

# Số lượng lớp
num_classes = 3

# Tạo ma trận nhầm lẫn
confusion_matrix = np.full((num_classes, num_classes), 0)

# Thêm các giá trị vào ma trận nhầm lẫn
confusion_matrix[0, 0] = 34
confusion_matrix[0, 1] = 1
confusion_matrix[1, 1] = 30
confusion_matrix[1, 0] = 2
confusion_matrix[2, 2] = 35
confusion_matrix[1, 2] = 3


# Tạo nhãn cho các trục
class_labels = ['acne', 'der', 'rw']

# Vẽ biểu đồ confusion matrix
plt.imshow(confusion_matrix, cmap='Blues',
           alpha=0.7)  # Giảm độ đậm của màu blue đi 15%
plt.title('Teachable Machine')
plt.xlabel('Prediction')
plt.ylabel('Class')
plt.xticks(np.arange(num_classes), class_labels)
plt.yticks(np.arange(num_classes), class_labels)

# Tùy chỉnh màu sắc của các ô
for i in range(num_classes):
    for j in range(num_classes):
        if i == j:
            # Đặt màu nhạt hơn cho các ô chính
            plt.text(j, i, str(
                confusion_matrix[i, j]), color='black', fontsize=12, ha='center', va='center')
        else:
            # Giữ nguyên màu sắc cho các ô còn lại
            # confusion_matrix[i, j] = 0
            plt.text(j, i, str(
                confusion_matrix[i, j]), color='black', fontsize=12, ha='center', va='center')

plt.show()
