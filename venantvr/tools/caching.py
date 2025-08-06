import functools

import json
import pickle
from functools import wraps


def cache_to_pickle(path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with open(path, 'rb') as pickle_file:
                    cached_result = pickle.load(pickle_file)
            except FileNotFoundError:
                cached_result = None
            if cached_result is not None:
                return cached_result
            else:
                result = func(*args, **kwargs)
                with open(path, 'wb') as pickle_file:
                    # noinspection PyTypeChecker
                    pickle.dump(result, pickle_file)
                return result

        return wrapper

    return decorator


def cache_to_json(path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with open(path, 'r') as json_file:
                    cached_result = json.load(json_file)
            except FileNotFoundError:
                cached_result = None
            if cached_result is not None:
                return cached_result
            else:
                result = func(*args, **kwargs)
                with open(path, 'w') as json_file:
                    # noinspection PyTypeChecker
                    json.dump(result, json_file, indent=2)
                return result

        return wrapper

    return decorator


def cache_for_n_calls(n):
    """
    Décorateur pour cacher le résultat d'une méthode pendant 'n' appels,
    avec un mécanisme de désactivation externe.

    :param n: Nombre d'appels pendant lequel le cache est actif.
    """

    def decorator(func):
        cached_result = None  # Pour stocker le résultat de la méthode
        call_count = 0  # Compteur d'appels

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal call_count, cached_result

            # Si le compteur est en dessous de 'n', retourner le résultat mis en cache
            if call_count % n != 0:
                call_count += 1
                return cached_result

            # Sinon, réinitialiser le compteur et recalculer le résultat
            call_count = 1  # Réinitialisation après recalcul
            cached_result = func(*args, **kwargs)
            return cached_result

        return wrapper

    return decorator
