import tensorflow as tf

def softmax_cross_entropy_with_logits(y_true, y_pred):
    return tf.nn.softmax_cross_entropy_with_logits_v2(labels=y_true, logits=y_pred)