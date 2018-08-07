"""Parameters used for the experiments of the paper."""

import tensorflow as tf

from scnn import utils


def get_params(ntrain, EXP_NAME, order, Nside):

    n_classes = 2

    params = dict()
    params['dir_name'] = EXP_NAME

    # Types of layers.
    params['conv'] = 'chebyshev5'  # Graph convolution: chebyshev5 or monomials.
    params['pool'] = 'max'  # Pooling: max or average.
    params['activation'] = 'relu'  # Non-linearity: relu, elu, leaky_relu, softmax, tanh, etc.
    params['statistics'] = 'mean'  # Statistics (for invariance): None, mean, var, meanvar, hist.

    # Architecture.
    params['F'] = [16, 32, 64, 64, 64, n_classes]  # Graph convolutional layers: number of feature maps.
    params['K'] = [2] * 6  # Polynomial orders.
    params['batch_norm'] = [True] * 6  # Batch normalization.
    params['M'] = []  # Fully connected layers: output dimensionalities.

    # Pooling.
    nsides = [Nside, Nside//2, Nside//4, Nside//8, Nside//16, Nside//32, Nside//32]
    print('#sides: {}'.format(nsides))
    print('#pixels: {}'.format([(nside//order)**2 for nside in nsides]))
    # Number of pixels on the full sphere: 12 * nsides**2.
    indexes = utils.nside2indexes(nsides, order)
    params['nsides'] = nsides
    params['indexes'] = indexes

    # Regularization (to prevent over-fitting).
    params['regularization'] = 0  # Amount of L2 regularization over the weights (will be divided by the number of weights).
    params['dropout'] = 1  # Percentage of neurons to keep.

    # Training.
    params['num_epochs'] = 60  # Number of passes through the training data.
    params['batch_size'] = 16 * order**2  # Constant quantity of information (#pixels) per step (invariant to sample size).
    print('#samples per batch: {}'.format(params['batch_size']))
    print('=> #pixels per batch (input): {:,}'.format(params['batch_size']*(Nside//order)**2))
    print('=> #pixels for training (input): {:,}'.format(params['num_epochs']*ntrain*(Nside//order)**2))

    # Optimization: learning rate schedule and optimizer.
    params['scheduler'] = lambda step: tf.train.exponential_decay(2e-2, step, decay_steps=3, decay_rate=0.98)
    params['optimizer'] = lambda lr: tf.train.MomentumOptimizer(lr, momentum=0.9, use_nesterov=True)
    # Adam alternative. More variance on final validation accuracy. Requires about 80 epochs.
    # params['scheduler'] = lambda step: tf.train.exponential_decay(2e-4, step, decay_steps=20, decay_rate=0.98)
    # params['optimizer'] = lambda lr: tf.train.AdamOptimizer(lr, beta1=0.9, beta2=0.999, epsilon=1e-8)
    n_steps = params['num_epochs'] * ntrain // params['batch_size']
    lr_max, lr_min = params['scheduler']([0, n_steps]).eval(session=tf.Session())
    print('Learning rate will start at {:.1e} and finish at {:.1e}.'.format(lr_max, lr_min))

    # Number of model evaluations during training (influence training time).
    n_evaluations = 200
    params['eval_frequency'] = int(params['num_epochs'] * ntrain / params['batch_size'] / n_evaluations)

    return params
