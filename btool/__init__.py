
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
  def __init__(self, cargo_target_triple, dotnet_runtime_target, exe_extension, ):
    self.cargo_target_triple = cargo_target_triple
    self.dotnet_runtime_target = dotnet_runtime_target
    self.exe_extension = exe_extension

  # For each build tool we define constants for cross-compilation;
  # at no point do we want to be reliant on some "default" configuration to build the SW
  LINUX_x64 = 'x86_64-unknown-linux-gnu', 'linux-x64', '',
  WINDOWS_x64 = 'x86_64-pc-windows-gnu', 'win-x64', '.exe',
  OSX_x64 = 'x86_64-apple-darwin', 'osx-x64', '',

def get_ui_exe(target: Target):
  return os.path.abspath(os.path.join(
    'vuf-gui', 'bin', 'Release', 'net6.0', target.dotnet_runtime_target, 'publish', 'vuf-gui'+target.exe_extension
  ))

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


def build_vuf_gui(target: Target):
  in_dir('vuf-gui',
    cmd_l('dotnet', 'publish', '--self-contained', '--configuration', 'Release', '--runtime', target.dotnet_runtime_target ),
  )

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
  
  print('Building VUF for targets={}'.format(targets_to_build))

  for target in targets_to_build:
    build_vuf_gui(target)


  if 'run' in args:
    cmd(
      get_ui_exe(Target.get_host_target()),
    )






