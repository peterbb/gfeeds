LIBEXEC_DIR = join_paths(get_option('prefix'), get_option('libexecdir'))
EXTENSION_DIR = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())

glade_conf = configuration_data()
glade_conf.set('PACKAGE_URL', website)
glade_conf.set('DATA_DIR', pkgdatadir)
glade_conf.set('EXTENSION_DIR', EXTENSION_DIR)
glade_conf.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
glade_conf.set('PYTHON_DIR', pythondir)
glade_conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
glade_conf.set('PYTHON', python_bin.path()) # python_bin defined in data/meson.build
glade_conf.set('APPID', app_id)
glade_conf.set('libexecdir', LIBEXEC_DIR)
# this is for development version # glade_conf.set('VERSION', ''.join([run_command(['git', 'describe', '--long', '--tags']).stdout(), get_option('profile')]))
glade_conf.set('VERSION', meson.project_version())
glade_conf.set('CONTRIBUTORS', contributors)
glade_conf.set('TRANSLATORS', translators)
glade_conf.set('authorfullname', authorfullname)
glade_conf.set('prettyname', prettyname)

# this has been moved to /data/meson.build
#configure_file(
#    input: 'aboutdialog.glade.in',
#    output: 'aboutdialog.glade',
#    configuration: glade_conf
#)
