import tensorflow as tf
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.vgg19 import preprocess_input

def L1_loss(x, y):
    return tf.reduce_mean(tf.abs(x - y))

def L2_loss(x, y):
    return tf.reduce_mean(tf.square(x - y))

def Huber_loss(x, y, delta=1.0):
    return tf.keras.losses.Huber(delta=delta)(x, y)

def regularization_loss(model, name_scope):
    losses = []
    for loss in model.losses:
        if name_scope in loss.name:
            losses.append(loss)
    return tf.add_n(losses) if losses else tf.constant(0.0)

def generator_loss(fake):
    return tf.reduce_mean(tf.square(fake - 0.9))

def discriminator_loss(anime_logit, fake_logit):
    # LSGAN loss
    anime_gray_logit_loss = tf.reduce_mean(tf.square(anime_logit - 0.9))
    fake_gray_logit_loss = tf.reduce_mean(tf.square(fake_logit - 0.1))
    loss = 0.5 * anime_gray_logit_loss + 1.0 * fake_gray_logit_loss
    return loss

def discriminator_loss_346(fake_logit):
    # LSGAN loss
    fake_logit_loss = tf.reduce_mean(tf.square(fake_logit - 0.1))
    loss = 1.0 * fake_logit_loss
    return loss

def discriminator_loss_m(real, fake):
    real_loss = tf.reduce_mean(tf.square(real - 1.))
    fake_loss = tf.reduce_mean(tf.square(fake))
    loss = real_loss + fake_loss
    return loss

def generator_loss_m(fake):
    return tf.reduce_mean(tf.square(fake - 1.))

def gram(x):
    shape_x = tf.shape(x)
    b = shape_x[0]
    c = shape_x[3]
    x = tf.reshape(x, [b, -1, c])
    return tf.matmul(tf.transpose(x, [0, 2, 1]), x) / tf.cast((tf.size(x) // b), tf.float32)

def create_vgg19_feature_extractor(layer_names=None):
    """
    Create a VGG19 feature extractor.
    
    Args:
        layer_names (list, optional): List of layer names to extract features from.
            If None, uses default layers: 
            ['block1_conv2', 'block2_conv2', 'block3_conv2', 'block4_conv2', 'block5_conv2']
    
    Returns:
        A Keras Model that outputs features from specified layers
    """
    if layer_names is None:
        layer_names = [
            'block1_conv2', 'block2_conv2', 'block3_conv2', 
            'block4_conv2', 'block5_conv2'
        ]
    
    # Load VGG19 without top layers, weights pre-trained on ImageNet
    base_model = VGG19(weights='imagenet', include_top=False)
    
    # Create a model that outputs features from specified layers
    outputs = [base_model.get_layer(name).output for name in layer_names]
    return tf.keras.Model(inputs=base_model.input, outputs=outputs)

def VGG_LOSS(x, y, vgg19=None):
    """
    Compute VGG loss between x and y using feature representations.
    
    Args:
        x (tensor): First input tensor
        y (tensor): Second input tensor
        vgg19 (tf.keras.Model, optional): VGG19 feature extractor. 
                                          If None, a default extractor is created.
    
    Returns:
        Scalar loss value
    """
    if vgg19 is None:
        vgg19 = create_vgg19_feature_extractor()
    
    # Preprocess inputs (important for using pre-trained VGG)
    x_preprocessed = preprocess_input(x)
    y_preprocessed = preprocess_input(y)
    
    # Extract features
    x_features = vgg19(x_preprocessed)
    y_features = vgg19(y_preprocessed)
    
    # Compute L1 loss between features
    if isinstance(x_features, list):
        # If multiple layers are extracted
        return tf.reduce_mean([
            L1_loss(x_feat, y_feat) / tf.cast(tf.size(x_feat), tf.float32)
            for x_feat, y_feat in zip(x_features, y_features)
        ])
    else:
        # Single layer extraction
        return L1_loss(x_features, y_features) / tf.cast(tf.size(x_features), tf.float32)

def con_loss(real, fake, vgg19=None, weight=1.0):
    """Content loss using VGG feature comparison"""
    return weight * VGG_LOSS(real, fake, vgg19)

def region_smoothing_loss(seg, fake, vgg19=None, weight=1.0):
    """Region smoothing loss using VGG features"""
    return VGG_LOSS(seg, fake, vgg19) * weight

def style_loss(style, fake, vgg19=None, weight=1.0):
    """
    Style loss computation using Gram matrix of VGG features.
    
    Args:
        style (tensor): Style input tensor
        fake (tensor): Generated tensor
        vgg19 (tf.keras.Model, optional): VGG19 feature extractor
        weight (float, optional): Loss weight
    
    Returns:
        Scalar style loss
    """
    if vgg19 is None:
        vgg19 = create_vgg19_feature_extractor()
    
    # Preprocess inputs
    style_preprocessed = preprocess_input(style)
    fake_preprocessed = preprocess_input(fake)
    
    # Extract features
    style_feat = vgg19(style_preprocessed)
    fake_feat = vgg19(fake_preprocessed)
    
    # Compute Gram matrices and L1 loss
    return weight * L1_loss(gram(style_feat), gram(fake_feat)) / tf.cast(tf.size(style_feat), tf.float32)

def style_loss_decentralization_3(style, fake, vgg19=None, weight=None):
    """
    Multi-layer style loss with feature decentralization.
    
    Args:
        style (tensor): Style input tensor
        fake (tensor): Generated tensor
        vgg19 (tf.keras.Model, optional): VGG19 feature extractor
        weight (list, optional): Weights for different layer losses
    
    Returns:
        Tuple of style losses for different layers
    """
    if vgg19 is None:
        vgg19 = create_vgg19_feature_extractor([
            'block2_conv2', 'block3_conv2', 'block4_conv2'
        ])
    
    if weight is None:
        weight = [1.0, 1.0, 1.0]
    
    # Preprocess inputs
    style_preprocessed = preprocess_input(style)
    fake_preprocessed = preprocess_input(fake)
    
    # Extract multi-layer features
    style_features = vgg19(style_preprocessed)
    fake_features = vgg19(fake_preprocessed)
    
    # Compute decentralized losses
    losses = []
    for style_feat, fake_feat, w in zip(style_features, fake_features, weight):
        # Subtract mean along spatial dimensions
        style_feat_centered = style_feat - tf.reduce_mean(style_feat, axis=[1, 2], keepdims=True)
        fake_feat_centered = fake_feat - tf.reduce_mean(fake_feat, axis=[1, 2], keepdims=True)
        
        # Compute loss
        loss = L1_loss(gram(style_feat_centered), gram(fake_feat_centered)) / tf.cast(tf.size(style_feat), tf.float32)
        losses.append(w * loss)
    
    return tuple(losses)