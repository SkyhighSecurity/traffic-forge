"""
Numpy compatibility layer for testing without numpy.

Provides simple replacements for numpy functions used in the codebase.
"""

import random
import math


def normal(mean, std):
    """Simple normal distribution using Box-Muller transform."""
    u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean + z0 * std


def exponential(scale):
    """Simple exponential distribution."""
    return -scale * math.log(random.random())


def gamma(shape, scale):
    """Simple gamma distribution approximation."""
    # Very basic approximation for testing
    return max(0, normal(shape * scale, math.sqrt(shape) * scale))


def exp(x):
    """Exponential function."""
    return math.exp(x)


def array(lst):
    """Simple array wrapper."""
    return lst


def choice(lst, size=1, replace=True, p=None):
    """Simple weighted choice."""
    if p is None:
        if size == 1:
            return random.choice(lst)
        return random.choices(lst, k=size)
    else:
        # Normalize probabilities
        total = sum(p)
        probs = [x/total for x in p]
        if size == 1:
            return random.choices(lst, weights=probs, k=1)[0]
        if replace:
            return random.choices(lst, weights=probs, k=size)
        else:
            # Simple non-replacement sampling
            result = []
            available = list(zip(lst, probs))
            for _ in range(size):
                if not available:
                    break
                choices, weights = zip(*available)
                idx = random.choices(range(len(choices)), weights=weights, k=1)[0]
                result.append(choices[idx])
                available.pop(idx)
            return result


# Create a namespace object to mimic numpy
class np:
    random = type('random', (), {
        'normal': normal,
        'exponential': exponential,
        'gamma': gamma,
        'choice': choice
    })()
    exp = exp
    array = array