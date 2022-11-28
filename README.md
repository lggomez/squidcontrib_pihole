# squidcontrib_pihole

### See README.orig for the Blacklists UT1 original README

## Overview

This project is an adaptation of Fabrice Prigent's **Blacklists UT1** project which is available at https://dsi.ut-capitole.fr/blacklists/index_en.php

While the project offers extensive flexibility for HTTP proxy solutions it lacks the DNS-list format that Pi-hole uses, making it not usable without a manual setup and hosting; Also the lists contain IPs, which Pi-hole does not aim to block

This repo consists of 3 parts:

* `/domains` directory: The main directory containing all sublists, as originally prepared by Fabrice, sans IPs and in text format, ready for Pihole consumption as Adlists
  * Some lists may be 'missing' from the original category list (https://dsi.ut-capitole.fr/blacklists/) since their parent directories are duplicates, thus being merged (i.e: malware and phishing share the _phishing_ directory)
  * **(OPTIONAL)** adults: too large and Github LFS complains, not my first use case. Remove in `exclusions` list at `downloader.py`
* **(OPTIONAL)** `/domains/the_whole_thing.txt`: The aggregate of _ALL_ lists. If for some reason you really wanna use this, go ahead, I saved you the trouble of building it. But be warned, it will break navigation for all practical purposes and has almost 10 million domains as of today (Nov 27). Also, some side points:
  * No duplicate detection was made (TODO?)
  * No certainty on how much is this going stress Pi-hole's core/gravity
  * To enable it set AGGREGATE = True on downloader.py and run
* `downloader.py`: This script is the core of this repo; it builds the beforementioned items. Should you have to fork this repo for some reason and provision your lists repository on your own, this script will download and rebuild the domain lists
  * Delete the previous `.tar.gz` files prior updating (TODO: automate this part)

## Usage

Lists in the `/domains` directory can be added by their raw link to Pi-hole by category:

###i.e: phishing:

```
https://media.githubusercontent.com/media/lggomez/squidcontrib_pihole/main/domains/phishing/domains.txt
```

## Dependencies

* Python 3.x
* Git LFS: https://git-lfs.github.com/
  * `git lfs install`
  * `git lfs track "*.txt"`

## License

See Blacklists UT1 license at `LICENSE.pdf` and `cc-by-sa-4-0.pdf`