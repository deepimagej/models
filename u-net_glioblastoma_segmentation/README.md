# Intended Use
A U-Net trained to segment cells in 2D images.

# Images used for training
- Microscopy modality: Phase contrast
- Data shape: 2D
- Cell type: Glioblastoma-astrocytoma (U373)
- Source: Cell Tracking Challenge

# Recommended validation metrics
- Jaccard index
- Hausdorff distance
- Binary Cross Entropy
- Precision, Recall and F1 over true and false positive pixels

# Training schedule
- Steps per epoch: 500
- Epochs: 10
- Learning rate: 1e−04
- Learning rate decay: 5e−07
- Loss function: Binary Cross Entropy (BCE)
- Images for training: 24
- Images for test: 10

# Quantitative Analyses
(Unitary results, Intersectional results)

- Binary cross entropy loss function (training): 0.061
- Binary cross entropy loss function (test): 0.054
- Accuracy (training): 0.985
- Accuracy (test): 0.984
- SEG measure (Cell Tracking Challenge) (test): 0.795

# Caveats and Recommendations
The model is provided as a usecase for deepImageJ. For its integration in image processing workflows it has should be fine-tuned and validated.
