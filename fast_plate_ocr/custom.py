"""
Custom metrics and loss functions.
"""

from keras import losses, metrics, ops

from fast_plate_ocr.config import MAX_PLATE_SLOTS, VOCABULARY_SIZE


def cat_acc(
    y_true,
    y_pred,
    max_plate_slots: int = MAX_PLATE_SLOTS,
    vocabulary_size: int = VOCABULARY_SIZE,
):
    """
    This is simply the CategoricalAccuracy for multi-class label problems. Example if the correct
    label is ABC123 and ABC133 is predicted, it will not give a precision of 0% like plate_acc
    (not completely classified correctly), but 83.3% (5/6).
    """
    y_true = ops.reshape(y_true, newshape=(-1, max_plate_slots, vocabulary_size))
    y_pred = ops.reshape(y_pred, newshape=(-1, max_plate_slots, vocabulary_size))
    return ops.mean(metrics.categorical_accuracy(y_true, y_pred))


def plate_acc(
    y_true,
    y_pred,
    max_plate_slots: int = MAX_PLATE_SLOTS,
    vocabulary_size: int = VOCABULARY_SIZE,
):
    """
    Compute how many plates were correctly classified. For a single plate, if ground truth is
    'ABC 123', and the prediction is 'ABC 123', then this would give a score of 1. If the prediction
     was ABD 123, it would score 0.
    """
    y_true = ops.reshape(y_true, newshape=(-1, max_plate_slots, vocabulary_size))
    y_pred = ops.reshape(y_pred, newshape=(-1, max_plate_slots, vocabulary_size))
    et = ops.equal(ops.argmax(y_true), ops.argmax(y_pred))
    return ops.mean(ops.cast(ops.all(et, axis=-1, keepdims=False), dtype="float32"))


def top_3_k(
    y_true,
    y_pred,
    vocabulary_size: int = VOCABULARY_SIZE,
):
    """
    Calculates how often the true character is found in the 3 predictions with the highest
    probability.
    """
    # Reshape into 2-d
    y_true = ops.reshape(y_true, (-1, vocabulary_size))
    y_pred = ops.reshape(y_pred, (-1, vocabulary_size))
    return ops.mean(metrics.top_k_categorical_accuracy(y_true, y_pred, k=3))


# Custom loss
def cce(
    y_true,
    y_pred,
    vocabulary_size: int = VOCABULARY_SIZE,
):
    """
    Computes the categorical cross-entropy loss.
    """
    y_true = ops.reshape(y_true, newshape=(-1, vocabulary_size))
    y_pred = ops.reshape(y_pred, newshape=(-1, vocabulary_size))
    return ops.mean(
        losses.categorical_crossentropy(y_true, y_pred, from_logits=False, label_smoothing=0.2)
    )