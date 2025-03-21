# encoding: utf-8
# nuitka-project: --include-data-dir=./TSAnalyzer/=TSAnalyzer
# nuitka-project: --windows-disable-console
# Compilation mode, standalone everywhere, except on macOS there app bundle

# nuitka-project-if: {OS} == "Darwin":
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --macos-app-icon==TSAnalyzer/resources/images/icon.ico


# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-icon-from-ico=TSAnalyzer/resources/images/icon.ico
# nuitka-project-if: {OS} == "Linux":
#    nuitka-project: --linux-icon=TSAnalyzer/resources/images/icon.ico

from TSAnalyzer import main

main()
