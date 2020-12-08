 # wpPluginsExplorer
<p align="center">
![version](https://img.shields.io/badge/version-0.1-blue) ![python](https://img.shields.io/badge/python-2.7-yellow)
![license](https://img.shields.io/badge/license-MIT-green)
</p>
<hr>

Contact: [v4lerio](https://twitter.com/valeriocestrone)

This is a "quick&dirty mass-scanner for Wordpress" Plugins. It is a "fork" of the improved version of `wordpricy.py` initially made by [CodySixteen](https://twitter.com/CodySixteen) on its Notes Magazine 01 the 20th Oct 2020. Code was in the README section encoded in base64.

Enjoy!
## Usage

### Download first 50 pages of WP popular plugins
```$ ./main.py```

> Please note that 50 pages of plugins are ~4.5GB uncompressed! 

> If only want to analyse specific plugins download them manually and put all files in `./plugins`, then ```$ ./main.py analyse```

### Analyse all php files within the plugins directory
```$ ./main.py analyse```

### Analyse all php files within the specified directory
```$ ./main.py analyse ./plugins/maintenance```

### Analyse all php files within the specified directory, show only some issues
```$ ./main.py analyse ./plugins/maintenance 3```

- level 1 = all
- level 2 = sqli and some RFI/LFI
- level 3 = only sqli

### RoadMap

- [ ] Set page as argument
- [ ] Set specific url/page to download
- [ ] Set specific plugin name to look for
- [ ] Improved argument parser
- [ ] Color coded output
- [ ] Stats/Summary only (no list of issues)
- [ ] Refactor code and comments
- [ ] Convert to Python3
- [ ] Improve regex and class identification

### Pull Requests (PR)

Feel free to submit PRs and let us know if you find intresting stuff or get some kudos/$$ using this tool :D 

Thank you
