# Python.Trading.Tools

## Description

`Python.Trading.Tools` est une bibliothèque utilitaire conçue pour simplifier les tâches de logging et de mise en cache dans les applications Python, particulièrement
dans le contexte du trading où la performance et la journalisation sont essentielles.

Cette bibliothèque fournit des décorateurs pour le cache et des fonctions pour une configuration de logging flexible.

## Installation

Cette bibliothèque est conçue pour être installée en tant que package Python.

```
pip install .
```

ou, si vous souhaitez l'installer en mode "editable" pour le développement :

```
pip install -e .
```

### Prérequis

* Python \>= 3.8

## Modules et fonctionnalités

### `caching.py`

Ce module fournit des décorateurs de fonction pour mettre en cache les résultats d'une méthode.

* `@cache_to_pickle(path)`: Met en cache le résultat d'une fonction dans un fichier `.pickle`. La fonction ne sera exécutée qu'une seule fois. Lors des appels suivants,
  le résultat sera chargé depuis le fichier.

* `@cache_to_json(path)`: Met en cache le résultat d'une fonction dans un fichier `.json`. Similaire à `@cache_to_pickle`, mais le résultat est stocké au format JSON.

* `@cache_for_n_calls(n)`: Met en cache le résultat d'une fonction pour `n` appels consécutifs. La fonction sera ré-exécutée au `n`-ième appel, et son nouveau résultat
  sera mis en cache pour les `n` appels suivants.

### `logger.py` et `stream.py`

Ces modules fournissent des outils pour une configuration de logging robuste.

* `setup_logging(log_level)`: Configure le logger principal de l'application, en définissant le niveau de log et en créant un `StreamHandler` pour afficher les logs dans
  la console. Cette fonction redirige également `sys.stdout` et `sys.stderr` vers le logger, ce qui est très utile pour capturer toutes les sorties (y compris les
  `print()`) dans les logs.

* `configure_stream(runtime_logger, log_file)`: Ajoute un `WatchedFileHandler` au logger, permettant de sauvegarder les logs dans un fichier spécifié. Il s'assure que le
  répertoire de destination existe.

* `logger`: Une instance de logger pré-configurée par défaut.

* `StreamToLogger`: Une classe utilitaire interne utilisée pour rediriger les flux de sortie standard vers le logger.

## Utilisation

### Logging

```
from venantvr.tools import setup_logging, configure_stream, logger
import sys

# Configure le logger principal avec le niveau DEBUG
main_logger = setup_logging(log_level=logging.DEBUG)

# Ajoute un handler pour écrire les logs dans un fichier
configure_stream(main_logger, "logs/app.log")

# Utilisation des logs
main_logger.info("Démarrage de l'application...")
main_logger.debug("Ceci est un message de débogage.")
main_logger.error("Une erreur est survenue !")

# Les appels à print sont aussi capturés
print("Ceci sera affiché dans le logger.")

# Pour un autre logger
# from logging import getLogger
# my_module_logger = getLogger("my_module")
# my_module_logger.info("Un message de mon_module.")
```

### Mise en cache

```
from venantvr.tools import cache_to_pickle, cache_to_json, cache_for_n_calls
import time

# Exemple avec cache_to_pickle
@cache_to_pickle('data_cache.pkl')
def get_heavy_data_pickle():
    print("Fetching data (pickle)...")
    time.sleep(2)
    return {"id": 1, "value": "heavy data"}

# Le premier appel prendra 2 secondes, les suivants seront instantanés
data = get_heavy_data_pickle()
print(data)
data = get_heavy_data_pickle()
print(data)

# Exemple avec cache_to_json
@cache_to_json('data_cache.json')
def get_heavy_data_json():
    print("Fetching data (json)...")
    time.sleep(2)
    return {"id": 2, "value": "another heavy data"}

# Le premier appel prendra 2 secondes, les suivants seront instantanés
data = get_heavy_data_json()
print(data)
data = get_heavy_data_json()
print(data)

# Exemple avec cache_for_n_calls
@cache_for_n_calls(n=3)
def get_market_price():
    current_time = time.time()
    print(f"Fetching fresh market price at {current_time}")
    return {"price": current_time}

# Le prix sera mis en cache pendant 3 appels
for _ in range(5):
    price_info = get_market_price()
    print(price_info)
    time.sleep(1)
```
