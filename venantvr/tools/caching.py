import functools

import json
import os
import pickle
from functools import wraps
from pathlib import Path


def dynamic_cache_to_json(template_dir):
    """
    Un décorateur qui génère un chemin de fichier de cache dynamique
    basé sur les attributs de l'instance de la classe et crée l'arborescence si nécessaire.
    """

    """
    Décorateur générique pour cacher le résultat d'une fonction dans un fichier JSON.
    Le chemin de cache est construit à partir d'un template de répertoire et des propriétés de l'instance.

    :param template_dir: Un chemin de répertoire de cache avec des placeholders (ex: 'cache/{exchange_name}/').
                         Le nom du fichier est implicitement le nom de la fonction décorée.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Formater le chemin du répertoire avec toutes les propriétés de l'instance
            cache_dir = Path(template_dir.format(**self.__dict__))

            # Utiliser le nom de la fonction pour le nom du fichier
            cache_filename = f"{func.__name__}.json"
            cache_path = cache_dir / cache_filename

            # Créer l'arborescence des dossiers si elle n'existe pas
            os.makedirs(cache_dir, exist_ok=True)

            # Logique de chargement du cache
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as file:
                    return json.load(file)

            # Exécuter la fonction d'origine
            result = func(self, *args, **kwargs)

            # Logique de sauvegarde du cache
            with open(cache_path, 'w') as file:
                json.dump(result, file)

            return result

        return wrapper

    return decorator


def dynamic_cache_to_pickle(template_dir):
    """
    Décorateur générique pour cacher le résultat d'une fonction dans un fichier pickle.
    Le chemin de cache est construit à partir d'un template de répertoire et des propriétés de l'instance.

    :param template_dir: Un chemin de répertoire de cache avec des placeholders (ex: 'cache/{exchange_name}/').
                         Le nom du fichier est implicitement le nom de la fonction décorée.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Formater le chemin du répertoire avec toutes les propriétés de l'instance
            cache_dir = Path(template_dir.format(**self.__dict__))

            # Utiliser le nom de la fonction pour le nom du fichier
            cache_filename = f"{func.__name__}.pickle"
            cache_path = cache_dir / cache_filename

            # Créer l'arborescence des dossiers si elle n'existe pas
            os.makedirs(cache_dir, exist_ok=True)

            # Logique de chargement du cache
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as file:
                    return pickle.load(file)

            # Exécuter la fonction d'origine
            result = func(self, *args, **kwargs)

            # Logique de sauvegarde du cache
            with open(cache_path, 'wb') as file:
                # noinspection PyTypeChecker
                pickle.dump(result, file)

            return result

        return wrapper

    return decorator


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
