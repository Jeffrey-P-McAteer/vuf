
import os
import sys
import subprocess
import platform
import enum
import shutil

class Target(enum.Enum):
  @staticmethod
  def get_host_target():
    system = platform.system().lower()
    if system == 'windows':
      return Target.WINDOWS_x64
    elif system == 'darwin':
      return Target.OSX_x64
    elif system == 'linux':
      return Target.LINUX_x64
    else:
      raise Exception('Unknown platform.system().lower() = '+str(system))


  def __new__(cls, *args, **kwds):
    value = len(cls.__members__) + 1
    obj = object.__new__(cls)
    obj._value_ = value
    return obj
  def __init__(self, cargo_target_triple, dotnet_runtime_target, exe_file_name, shared_lib_file_name):
    self.cargo_target_triple = cargo_target_triple
    self.dotnet_runtime_target = dotnet_runtime_target
    self.exe_file_name = exe_file_name
    self.shared_lib_file_name = shared_lib_file_name

  # For each build tool we define constants for cross-compilation;
  # at no point do we want to be reliant on some "default" configuration to build the SW
  LINUX_x64 = 'x86_64-unknown-linux-gnu', 'linux-x64', 'vuf-gui', 'libvuf.so',
  WINDOWS_x64 = 'x86_64-pc-windows-gnu', 'win-x64', 'vuf-gui.exe', 'vuf.dll',
  OSX_x64 = 'x86_64-apple-darwin', 'osx-x64', 'vuf-gui', 'libvuf.dylib'

def in_dir(directory, *cmds):
  cwd = os.path.abspath( os.getcwd() )
  os.chdir(directory)
  try:
    for c in cmds:
      c()
  except:
    os.chdir(cwd)
    raise
  os.chdir(cwd)


def cmd(*pieces):
  exe_file = shutil.which(pieces[0])
  if exe_file is None:
    raise Exception('Please install the program "{}" which is required to build this component.'.format(pieces[0]))
  subprocess.run([str(exe_file), *list(pieces[1:]) ], check=True)

def cmd_l(*pieces):
  return lambda: cmd(*pieces)

def get_ui_exe(target: Target):
  return os.path.abspath(os.path.join(
    'vuf-gui', 'bin', 'Release', 'net6.0', target.dotnet_runtime_target, 'publish', target.exe_file_name
  ))

def build_vuf_gui(target: Target):
  in_dir('vuf-gui',
    cmd_l('dotnet', 'publish', '--self-contained', '--configuration', 'Release', '--runtime', target.dotnet_runtime_target ),
  )


def get_shared_lib(target: Target):
  return os.path.abspath(os.path.join(
    'vuf-lib', 'target', target.cargo_target_triple, 'release', target.shared_lib_file_name
  ))

def build_vuf_lib(target: Target):
  in_dir('vuf-lib',
    cmd_l('cargo', 'build', '--release', '--target', target.cargo_target_triple ),
  )


def write_cargo_config():
  config_f = os.path.join('.cargo', 'config')
  if not os.path.exists(os.path.dirname(config_f)):
    os.makedirs(os.path.dirname(config_f), exists_ok=True)

  if os.path.exists(config_f):
    return # Avoid re-work, assume existence means everything's fine.

  apple_linker = 'x86_64-apple-darwin20.4-clang'
  apple_ar = 'x86_64-apple-darwin20.4-ar'
  windows_linker = 'x86_64-w64-mingw32-gcc'
  windows_ar = 'x86_64-w64-mingw32-ar'
  
  for d in os.environ.get('PATH', '').split(os.pathsep):
    for file_name in os.listdir():
      if 'x86_64' in file_name and 'apple' in file_name and 'darwin' in file_name and ( file_name.endswith('gcc') or file_name.endswith('clang') ):
        apple_linker = file_name
      elif 'x86_64' in file_name and 'apple' in file_name and 'darwin' in file_name and file_name.endswith('ar'):
        apple_ar = file_name
      elif 'x86_64' in file_name and 'w64' in file_name and 'mingw32' in file_name and ( file_name.endswith('gcc') or file_name.endswith('clang') ):
        windows_linker = file_name
      elif 'x86_64' in file_name and 'w64' in file_name and 'mingw32' in file_name and file_name.endswith('ar'):
        windows_ar = file_name

  for tool in [apple_linker, apple_ar, windows_linker, windows_ar]:
    if shutil.which(tool) is None:
      raise Exception('Cannot find a tool we expected to have for cross-compilation: {}'.format(tool))

  with open(config_f, 'w') as fd:
    fd.write('''
[target.x86_64-apple-darwin]
linker = "{apple_linker}"
ar = "{apple_ar}"

[target.x86_64-pc-windows-gnu]
linker = "{windows_linker}"
ar = "{windows_ar}"

'''.format(
  apple_linker=apple_linker,
  apple_ar=apple_ar,
  windows_linker=windows_linker,
  windows_ar=windows_ar,
))

def select_only_one_target(args, targets):
  one_target = None
  for arg in args:
    for target in targets:
      if arg == target.cargo_target_triple or arg == target.dotnet_runtime_target:
        one_target = target
  return one_target


def main(args=sys.argv):
  targets_to_build = [
    Target.LINUX_x64, Target.WINDOWS_x64, Target.OSX_x64,
  ]

  # If the user passes 'run', only the host target is built
  if 'run' in args:
    targets_to_build = [ Target.get_host_target() ]

# For all properties of targets, if one is specified in args we only build that platform.
  # Default is to build for every supported target.
  one_target = select_only_one_target(args, targets_to_build)
  if not one_target is None:
    targets_to_build = [ one_target ]
  
  print('')
  print('Building VUF for targets={}'.format(targets_to_build))
  print('')

  write_cargo_config()

  for target in targets_to_build:
    print('')
    print('Building VUF for target={}'.format(target))
    print('')

    build_vuf_lib(target)
    build_vuf_gui(target)


  if 'run' in args:
    cmd(
      get_ui_exe(Target.get_host_target()),
    )






