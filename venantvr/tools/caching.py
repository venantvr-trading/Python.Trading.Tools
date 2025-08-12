import functools
import json
import os
import pickle
from functools import wraps
from pathlib import Path


def dynamic_cache_to_json(template_dir, cache_filename=None):
    """
    Décorateur générique pour cacher le résultat d'une fonction dans un fichier JSON.
    Le chemin de cache est construit à partir d'un template de répertoire et des propriétés de l'instance.

    :param template_dir: Un chemin de répertoire de cache avec des placeholders (ex: 'cache/{exchange_name}/').
    :param cache_filename: (Optionnel) Nom du fichier de cache. Par défaut, c'est le nom de la fonction décorée avec l'extension .json.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Formater le chemin du répertoire avec toutes les propriétés de l'instance
            cache_dir = Path(template_dir.format(**self.__dict__))

            # Utiliser le nom de fichier optionnel, sinon le nom de la fonction
            final_cache_filename = cache_filename if cache_filename else f"{func.__name__}.json"
            cache_path = cache_dir / final_cache_filename

            # Créer l'arborescence des dossiers si elle n'existe pas
            os.makedirs(cache_dir, exist_ok=True)

            # Logique de chargement du cache
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as file:
                    cached_data = json.load(file)
                    # Retourner l'objet mis en cache
                    return cached_data.get("value")

            # Exécuter la fonction d'origine
            result = func(self, *args, **kwargs)

            # Logique de sauvegarde du cache
            with open(cache_path, 'w') as file:
                # Encapsuler le résultat dans un dictionnaire avec la clé "value"
                json.dump({"value": result}, file)

            return result

        return wrapper

    return decorator


def dynamic_cache_to_pickle(template_dir, cache_filename=None):
    """
    Décorateur générique pour cacher le résultat d'une fonction dans un fichier pickle.
    Le chemin de cache est construit à partir d'un template de répertoire et des propriétés de l'instance.

    :param template_dir: Un chemin de répertoire de cache avec des placeholders (ex: 'cache/{exchange_name}/').
    :param cache_filename: (Optionnel) Nom du fichier de cache. Par défaut, c'est le nom de la fonction décorée avec l'extension .pickle.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Formater le chemin du répertoire avec toutes les propriétés de l'instance
            cache_dir = Path(template_dir.format(**self.__dict__))

            # Utiliser le nom de fichier optionnel, sinon le nom de la fonction
            final_cache_filename = cache_filename if cache_filename else f"{func.__name__}.pickle"
            cache_path = cache_dir / final_cache_filename

            # Créer l'arborescence des dossiers si elle n'existe pas
            os.makedirs(cache_dir, exist_ok=True)

            # Logique de chargement du cache
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as file:
                    cached_data = pickle.load(file)
                    # Retourner l'objet mis en cache
                    return cached_data.get("value")

            # Exécuter la fonction d'origine
            result = func(self, *args, **kwargs)

            # Logique de sauvegarde du cache
            with open(cache_path, 'wb') as file:
                # Encapsuler le résultat dans un dictionnaire avec la clé "value"
                # noinspection PyTypeChecker
                pickle.dump({"value": result}, file)

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
