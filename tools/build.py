#!/usr/bin/env python

# Copyright 2015 Samsung Electronics Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import subprocess
import sys
from os import path
from check_tidy import check_tidy

TERM_RED = "\033[1;31m"
TERM_YELLOW = "\033[1;33m"
TERM_GREEN = "\033[1;32m"
TERM_BLUE = "\033[1;34m"
TERM_EMPTY = "\033[0m"

config_echo = True


def join_path(pathes):
    return path.abspath(reduce(lambda x, y: path.join(x, y), pathes))


def check_path(path):
    if not os.path.exists(path):
        return False
    return True


# Path for this script file.
 # should be <project_home>/tools.
SCRIPT_PATH = path.dirname(path.abspath(__file__))

# Home directory for the project.
ROOT = join_path([SCRIPT_PATH, '../'])

# Root directory for dependencies.
DEPS_ROOT = join_path([ROOT, 'deps'])

# Root directory for jerry script submodule.
JERRY_ROOT = join_path([DEPS_ROOT, 'jerry'])

# Root directory for libuv submodule.
LIBUV_ROOT = join_path([DEPS_ROOT, 'libuv'])

# Root directory for libtuv submodule.
LIBTUV_ROOT = join_path([DEPS_ROOT, 'libtuv'])

# Root directory for mraa submodule.
MRAA_ROOT = join_path([DEPS_ROOT, 'mraa'])

# Root directory for http-parser submodule.
HTTPPARSER_ROOT = join_path([DEPS_ROOT, 'http-parser'])

# Build directory suffix for jerry build.
JERRY_BUILD_SUFFIX = 'deps/jerry'

# Build direcrtory suffix for libuv build.
LIBUV_BUILD_SUFFIX = 'deps/libuv'

# Build direcrtory suffix for libtuv build.
LIBTUV_BUILD_SUFFIX = 'deps/libtuv'

# Build direcrtory suffix for http-parser build.
HTTPPARSER_BUILD_SUFFIX = 'deps/http-parser'

# Build direcrtory suffix for mraa build.
MRAA_BUILD_SUFFIX = 'deps/mraa'

# Root directory for the source files.
SRC_ROOT = join_path([ROOT, 'src'])

# Root directory for the include files.
INT_ROOT = join_path([ROOT, 'inc'])

# checktest
CHECKTEST = join_path([SCRIPT_PATH, 'check_test.py'])


def mkdir(path):
    if not check_path(path):
        os.makedirs(path)


def copy(src, dst):
    shutil.copy(src, dst);


def cmdline(cmd, args = []):
    cmd_line = cmd
    if len(args) > 0:
        cmd_line = cmd_line + " " + reduce(lambda x, y: x + " " + y, args)
    return cmd_line


def run_cmd(cmd, args = []):
    if config_echo:
        print
        print "%s%s%s" % (TERM_BLUE, cmdline(cmd, args), TERM_EMPTY)
        print
    return subprocess.call([cmd] + args)


def print_error(msg):
    print
    print "%s%s%s" % (TERM_RED, msg, TERM_EMPTY)
    print


def check_run_cmd(cmd, args = []):
    retcode = run_cmd(cmd, args)
    if retcode != 0:
        print_error("[Failed - %d] %s" % (retcode, cmdline(cmd, args)))
        exit(1)


def get_git_hash(path):
    os.chdir(path)
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()


def sys_name():
    name, _, _, _, _ = os.uname()
    return name.lower()


def sys_machine():
    _, _, _, _, machine = os.uname()
    return machine.lower()


options = {
    'buildtype': 'debug',
    'builddir': 'build',
    'buildlib': False,
    'target-arch': sys_machine(),
    'target-os': sys_name(),
    'target-board': '',
    'cmake-option': '',
    'make-flags': '-j',
    'nuttx-home': '',
    'init-submodule': True,
    'tidy': True,
    'jerry-memstats': False,
    'checktest': True,
    'jerry-heaplimit': 81,
    'tuv' : False,
    "mraa" : False,
}

boolean_opts = ['buildlib',
                'init-submodule',
                'tidy',
                'jerry-memstats',
                'checktest',
                'tuv',
                "mraa"]

def opt_build_type():
    return options['buildtype']

def opt_build_lib():
    return options['buildlib']

def opt_build_root():
    return join_path([ROOT,
                      options['builddir'],
                      opt_target_tuple(),
                      opt_build_type()])

def opt_build_libs():
    return join_path([opt_build_root(), 'libs'])

def opt_target_arch():
    return options['target-arch']

def opt_target_os():
    return options['target-os']

def opt_target_board():
    return options['target-board']

def opt_target_tuple():
    return opt_target_arch() + '-' + opt_target_os()

def opt_cmake_option():
    return options['cmake-option']

def opt_make_flags():
    return options['make-flags']

def opt_nuttx_home():
    return join_path([ROOT, options['nuttx-home']])

def opt_cmake_toolchain_file():
    return join_path([ROOT, 'cmake/config', opt_target_tuple() + '.cmake'])

def opt_init_submodule():
    return options['init-submodule']

def opt_tidy():
    return options['tidy']

def opt_jerry_memstats():
    return options['jerry-memstats']

def opt_checktest():
    return options['checktest']

def opt_jerry_heaplimit() :
    return options['jerry-heaplimit']

def opt_tuv():
    return options['tuv']

def opt_mraa():
    return options['mraa']


def parse_boolean_opt(name, arg):
    if arg.endswith(name):
        options[name] = False if arg.startswith('no') else True
        return True
    return False

def parse_args():
    for arg in sys.argv:
        optpair = arg.split('=', 1)
        opt = optpair[0][2:].lower()
        val = optpair[1] if len(optpair) == 2 else ""
        if opt == 'buildtype':
            if val.lower() == 'release':
                options[opt] = val.lower()
            elif val.lower() == 'debug':
                options[opt] = val.lower()
        elif opt == 'builddir':
            options[opt] = val
        elif opt == 'target-arch':
            if val.lower() in ['x86_64', 'i686', 'arm']:
                options[opt] = val.lower()
        elif opt == 'target-os':
            if val.lower() in ['linux', 'darwin', 'nuttx']:
                options[opt] = val.lower()
        elif opt == 'target-board':
            options[opt] = val
        elif opt == 'cmake-option':
            options[opt] = val
        elif opt == 'make-flags':
            options[opt] = val
        elif opt == 'nuttx-home':
            options[opt] = val
        elif opt == 'jerry-heaplimit':
            options[opt] = val
        else:
            for opt_name in boolean_opts:
                if parse_boolean_opt(opt_name, opt):
                    break
    if opt_build_type() == 'release':
        options['jerry-memstats'] = False;

def init_submodule():
    check_run_cmd('git', ['submodule', 'init'])
    check_run_cmd('git', ['submodule', 'update'])


def get_cache_path(cache_dir, libname, cache_hash):
    cache_path = join_path([cache_dir, libname + '.' + cache_hash])
    if not opt_init_submodule():
        cache_path += "-dirty"
    return cache_path


def check_cached(cache_path):
    if not opt_init_submodule():
        return False
    return check_path(cache_path)


def libuv_output_path():
    return join_path([opt_build_libs(), "libuv.a"])

def libtuv_output_path():
    return join_path([opt_build_libs(), "libtuv.a"])

def libhttpparser_output_path():
    return join_path([opt_build_libs(), "libhttpparser.a"])

def libmraa_output_path():
    return join_path([opt_build_libs(), "libmraa.so"])

def build_libuv():
    # check libuv submodule directory.
    if not check_path(LIBUV_ROOT):
        print '* libuv build failed - submodule not exists.'
        return False

    # get libuv get hash.
    git_hash = get_git_hash(LIBUV_ROOT)

    # libuv build directory.
    build_home = join_path([opt_build_root(), LIBUV_BUILD_SUFFIX])

    # libuv cached library.
    build_cache_dir = join_path([build_home, 'cache'])
    build_cache_path = get_cache_path(build_cache_dir, 'libuv', git_hash)

    # check if cache is available.
    if not check_cached(build_cache_path):
        # build libuv.

        # make build directory.
        mkdir(build_home)

        # change current directory to libuv.
        os.chdir(LIBUV_ROOT)

        # libuv is using gyp. run the system according to build target.
        if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
            check_run_cmd('./nuttx-configure', [opt_nuttx_home()])
        elif opt_target_arch() == 'arm' and opt_target_os() =='linux':
            check_run_cmd('./armlinux-configure')
        elif opt_target_arch() == 'i686':
            check_run_cmd('./gyp_uv.py', ['-f', 'make', '-Dtarget_arch=ia32'])
        else:
            check_run_cmd('./gyp_uv.py', ['-f', 'make'])

        # set build type.
        build_type = 'Release' if opt_build_type() == 'release' else 'Debug'

        # make libuv.
        check_run_cmd('make', ['-C',
                               'out',
                               'BUILDTYPE=' + build_type,
                               opt_make_flags()])

        # output: libuv.a
        output = join_path([LIBUV_ROOT, 'out', build_type, 'libuv.a'])

        # check if target is created.
        if not check_path(output):
            print '* libuv build failed - target not produced.'
            return False

        # copy output to cache
        mkdir(build_cache_dir)
        copy(output, build_cache_path)

    # copy cache to libs directory
    mkdir(opt_build_libs())
    copy(build_cache_path, libuv_output_path())

    return True

def build_libtuv():
    # check libtuv submodule directory.
    if not check_path(LIBTUV_ROOT):
        print '* libtuv build failed - submodule not exists.'
        return False

    # get libtuv get hash.
    git_hash = get_git_hash(LIBTUV_ROOT)

    # libtuv build directory.
    build_home = join_path([opt_build_root(), LIBTUV_BUILD_SUFFIX])

    # cached library.
    build_cache_dir = join_path([build_home, 'cache'])
    build_cache_path = get_cache_path(build_cache_dir, 'libtuv', git_hash)

    libtuv_cmake_opt = [LIBTUV_ROOT]

    libtuv_cmake_opt.append('-DCMAKE_TOOLCHAIN_FILE=' +
                            join_path([LIBTUV_ROOT, 'cmake/config/config_' +
                                      opt_target_tuple() + ".cmake"]))

    # check if cache is available.
    if not check_cached(build_cache_path):

        # make build directory.
        mkdir(build_home)

        # change current directory to libtuv.
        os.chdir(build_home)

        # set build type.
        build_type = opt_build_type()
        libtuv_cmake_opt.append("-DCMAKE_BUILD_TYPE=" + build_type)

        # set target
        target_platform = opt_target_tuple()
        libtuv_cmake_opt.append('-DTARGET_PLATFORM=' + target_platform)

        # for nuttx build.
        if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
            # system root
            libtuv_cmake_opt.append('-DTARGET_SYSTEMROOT=' + opt_nuttx_home())
            # target board
            libtuv_cmake_opt.append('-DTARGET_BOARD=' + opt_target_board())

        # lib output
        libtuvout = build_home
        libtuv_cmake_opt.append('-DLIBTUV_CUSTOM_LIB_OUT=' + libtuvout)

        # cmake and make
        check_run_cmd('cmake', libtuv_cmake_opt)
        check_run_cmd('make')
        output = join_path([build_home, 'libtuv.a'])

        # check if target is created.
        if not check_path(output):
            print '* libtuv build failed - target not produced.'
            return False

        # copy output to cache
        mkdir(build_cache_dir)
        copy(output, build_cache_path)

    # copy cache to libs directory
    mkdir(opt_build_libs())
    copy(build_cache_path, libtuv_output_path())

    return True


def is_need_fdlibm():
    return opt_target_arch() == 'arm' and opt_target_os() == 'nuttx'

def build_libjerry():
    # check libjerry submodule directory.
    if not check_path(JERRY_ROOT):
        print '* libjerry build failed - submodule not exists.'
        return False

    # get jerry git hash.
    git_hash = get_git_hash(JERRY_ROOT)

    # jerry build directory.
    build_home = join_path([opt_build_root(), JERRY_BUILD_SUFFIX])

    # jerry cached library.
    build_cache_dir = join_path([build_home, 'cache'])


    # build targets
    target_libjerry = {
        'name': 'jerrycore',
        'type_suffix': '',
        'target_name': 'jerry-core',
        'output_dir': 'jerry-core',
        'cache_path': get_cache_path(build_cache_dir, 'jerrycore', git_hash)
    }
    target_libjerry_ms = {
        'name': 'jerrycore',
        'type_suffix': '-mem_stats',
        'target_name': 'jerry-core',
        'output_dir': 'jerry-core',
        'cache_path': get_cache_path(build_cache_dir, 'jerrycore', git_hash)
    }
    target_libfdlibm = {
        'name': 'fdlibm',
        'type_suffix': '',
        'target_name': 'jerry-fdlibm.third_party.lib',
        'output_dir': 'third-party/fdlibm/',
        'cache_path': get_cache_path(build_cache_dir, 'fdlibm', git_hash)
    }

    if opt_jerry_memstats():
        target_list = [target_libjerry_ms]
    else:
        target_list = [target_libjerry]

    if is_need_fdlibm():
        target_list.append(target_libfdlibm)


    # check if cache is available.
    if any(not check_cached(t['cache_path']) for t in target_list):
        # build jerry.

        # make build directory.
        mkdir(build_home)

        # change current directory to build directory.
        os.chdir(build_home)

        # libjerry is using cmake.
        # prepare cmake command line option.
        jerry_cmake_opt = [JERRY_ROOT]

        # set lto off.
        jerry_cmake_opt.append('-DENABLE_LTO=OFF')

        # tool chain file.
        jerry_cmake_opt.append('-DCMAKE_TOOLCHAIN_FILE=' +
                               opt_cmake_toolchain_file())


        # for nuttx build.
        if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
            # nuttx include path.
            jerry_cmake_opt.append('-DEXTERNAL_LIBC_INTERFACE=' +
                                   join_path([opt_nuttx_home(), 'include']))
            jerry_cmake_opt.append('-DEXTERNAL_CMAKE_SYSTEM_PROCESSOR=arm')
            jerry_cmake_opt.append('-DEXTERNAL_MEM_HEAP_SIZE_KB=' +
                                   str(opt_jerry_heaplimit()))
        elif opt_target_arch() == 'arm' and opt_target_os() =='linux':
            jerry_cmake_opt.append('-DUSE_COMPILER_DEFAULT_LIBC=YES')

        # run cmake.
        # FIXME: Running cmake once cause a problem because cmake does not know
        # the system like "System is unknown to cmake". and the other settings
        # are not applied intendly, running twice solves the problem.
        check_run_cmd('cmake', jerry_cmake_opt)
        check_run_cmd('cmake', jerry_cmake_opt)

        # cmake will produce a Makefile.

        # run make for each target
        for target in target_list:

            build_target = '%s%s.%s' % (opt_build_type(), target['type_suffix'],
                                        target['target_name'])

            check_run_cmd('make', ['-C',
                                   build_home,
                                   build_target,
                                   opt_make_flags()])

            output = join_path([build_home,
                                target['output_dir'],
                               'lib' + build_target + '.a'])

            # check if target is created.
            if not check_path(output):
                print 'Jerry target %s build failed' % target['name']
                return False

            # copy output to cache
            mkdir(build_cache_dir)
            copy(output, target['cache_path'])

    # copy cache to libs directory
    mkdir(opt_build_libs())
    for target in target_list:
        dest = join_path([opt_build_libs(), 'lib' + target['name'] +'.a'])
        copy(target['cache_path'], dest)

    return True

def build_libhttpparser():
    # check http-parser submodule directory.
    if not check_path(HTTPPARSER_ROOT):
        print '* libhttpparser build failed - submodule not exists.'
        return False

    # get hash.
    git_hash = get_git_hash(HTTPPARSER_ROOT)

    # build directory.
    build_home = join_path([opt_build_root(), HTTPPARSER_BUILD_SUFFIX])

    # cached library.
    build_cache_dir = join_path([build_home, 'cache'])
    build_cache_path = get_cache_path(build_cache_dir, 'libhttpparser',
                                      git_hash)

    httpparser_cmake_opt = [HTTPPARSER_ROOT]

    if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
        httpparser_cmake_opt.append('-DNUTTX_HOME=' + opt_nuttx_home())
        httpparser_cmake_opt.append('-DOS=NUTTX')
        options['buildlib'] = True
    else:
        httpparser_cmake_opt.append('-DOS=LINUX')

    httpparser_cmake_opt.append('-DCMAKE_TOOLCHAIN_FILE=' +
                           opt_cmake_toolchain_file())

    # check if cache is available.
    if not check_cached(build_cache_path):

        # make build directory.
        mkdir(build_home)

        # change current directory to libuv.
        #os.chdir(HTTPPARSER_ROOT)
        os.chdir(build_home)

        # set build type.
        build_type = 'Release' if opt_build_type() == 'release' else 'Debug'

        httpparser_cmake_opt.append('-DBUILDTYPE=' + build_type)

        # cmake
        check_run_cmd('cmake', httpparser_cmake_opt)
        check_run_cmd('cmake', httpparser_cmake_opt)

        check_run_cmd('make')

        output = join_path([build_home,
                            'libhttpparser.a'])

        # check if target is created.
        if not check_path(output):
            print '* libhttpparser build failed - target not produced.'
            return False

        # copy output to cache
        mkdir(build_cache_dir)
        copy(output, build_cache_path)

    # copy cache to libs directory
    mkdir(opt_build_libs())
    copy(build_cache_path, libhttpparser_output_path())

    return True


def build_libmraa():
    # check mraa submodule directory.
    if not check_path(MRAA_ROOT):
        print '* mraa build failed - submodule not exists.'
        return False

    # get hash.
    git_hash = get_git_hash(MRAA_ROOT)

    # build directory.
    build_home = join_path([opt_build_root(), MRAA_BUILD_SUFFIX])

    # cached library.
    build_cache_dir = join_path([build_home, 'cache'])
    build_cache_path = get_cache_path(build_cache_dir, 'libmraa',
                                      git_hash)

    mraa_cmake_opt = [MRAA_ROOT]

    if opt_target_arch() == 'arm':
        mraa_cmake_opt.append("-DBUILDARCH=arm")
    elif opt_target_arch() == 'i686':
        mraa_cmake_opt.append("-DCMAKE_CXX_FLAGS=-m32")
        mraa_cmake_opt.append("-DCMAKE_C_FLAGS=-m32")

    # check if cache is available.
    if not check_cached(build_cache_path):

        # make build directory.
        mkdir(build_home)

        # change current directory to libuv.
        #os.chdir(MRAA_ROOT)
        os.chdir(build_home)

        # set build type.
        build_type = 'Release' if opt_build_type() == 'release' else 'Debug'

        mraa_cmake_opt.append('-DBUILDTYPE=' + build_type)

        # cmake
        check_run_cmd('cmake', mraa_cmake_opt)
        check_run_cmd('cmake', mraa_cmake_opt)

        check_run_cmd('make')

        output = join_path([build_home,
                            'src/'
                            'libmraa.so'])

        # check if target is created.
        if not check_path(output):
            print '* libmraa build failed - target not produced.'
            return False

        # copy output to cache
        mkdir(build_cache_dir)
        copy(output, build_cache_path)

    # copy cache to libs directory
    mkdir(opt_build_libs())
    copy(build_cache_path, libmraa_output_path())

    return True


def build_iotjs():
    os.chdir(SCRIPT_PATH)
    check_run_cmd('python', ['js2c.py', opt_build_type()])

    # iot.js build directory.
    build_home = join_path([opt_build_root(), 'iotjs'])
    mkdir(build_home)

    # set build type.
    build_type = 'Release' if opt_build_type() == 'release' else 'Debug'

    # build iotjs.

    # change current directory to build home.
    os.chdir(build_home)

    # IoT.js is using cmake.
    # prepare cmake command line option.
    iotjs_cmake_opt = [ROOT, "-DCMAKE_BUILD_TYPE=" + build_type]

    # set toolchain file.
    iotjs_cmake_opt.append('-DCMAKE_TOOLCHAIN_FILE=' +
                           opt_cmake_toolchain_file())

    # give target-os to include appropriate files in libtuv include
    if opt_tuv():
        iotjs_cmake_opt.append('-DTARGET_OS=' + opt_target_os())
        iotjs_cmake_opt.append('-DWITH_TUV=YES')

    # for nuttx build.
    if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
        iotjs_cmake_opt.append('-DNUTTX_HOME=' + opt_nuttx_home())
        options['buildlib'] = True

    if opt_build_lib():
        iotjs_cmake_opt.append('-DBUILD_TO_LIB=YES')

    # this will define 'ENABLE_JERRY_MEM_STATS' at config.cmake
    if opt_jerry_memstats():
        iotjs_cmake_opt.append('-DJERRY_MEM_STATS=YES')

    if opt_target_board():
        iotjs_cmake_opt.append('-DTARGET_BOARD=' + opt_target_board())

    if opt_mraa():
        iotjs_cmake_opt.append('-DWITH_MRAA=' + opt_target_board())

    if opt_cmake_option():
        iotjs_cmake_opt.append(opt_cmake_option())

    # run cmake
    # FIXME: Running cmake once cause a problem because cmake does not know the
    # system like "System is unknown to cmake". and the other settings are not
    # applied intendly, running twice solves the problem.
    check_run_cmd('cmake', iotjs_cmake_opt)
    check_run_cmd('cmake', iotjs_cmake_opt)

    # run make
    check_run_cmd('make', [opt_make_flags()])

    return True


def run_checktest():
    # iot.js executable
    iotjs = join_path([opt_build_root(), 'iotjs', 'iotjs'])
    return run_cmd(CHECKTEST, [iotjs]) == 0


# parse arguments.
parse_args()

print('=======================================')
for opt_key in options:
    print ' -', opt_key, ':', options[opt_key]
print

# tidy check.
if opt_tidy():
    if not check_tidy(ROOT):
        print_error("Failed check_tidy")
        sys.exit(1)

# init submodules.
if opt_init_submodule():
    init_submodule()

# make build directory.
mkdir(opt_build_root())

# build libtuv or libuv
if opt_tuv():
    if not build_libtuv():
        print_error("Failed build_libtuv")
        sys.exit(1)
else:
    if not build_libuv():
        print_error("Failed build_libuv")
        sys.exit(1)

# build jerry lib.
if not build_libjerry():
    print_error("Failed build_libjerry")
    sys.exit(1)

# build lib.
if not build_libhttpparser():
    sys.exit(1)

# build libmraa.
if opt_mraa():
    if not build_libmraa():
        print_error("Failed build_libmraa")
        sys.exit(1)

# build iot.js
if not build_iotjs():
    print_error("Failed build_iotjs")
    sys.exit(1)

# if nuttx, copy libraries to lib folder of nuttx
if opt_target_arch() == 'arm' and opt_target_os() =='nuttx':
    nuttx_lib = join_path([opt_nuttx_home(), 'lib'])

    copy(libhttpparser_output_path(), nuttx_lib)
    if opt_tuv():
        copy(libtuv_output_path(), nuttx_lib)
    else:
        copy(libuv_output_path(), nuttx_lib)

    libjerry_output_path = join_path([opt_build_libs(), 'libjerrycore.a'])
    copy(libjerry_output_path, nuttx_lib)

    libfdlibm_output_path = join_path([opt_build_libs(), 'libfdlibm.a'])
    copy(libfdlibm_output_path, nuttx_lib)

    iotjs_output_path = join_path([opt_build_root(), 'iotjs', 'liblibiotjs.a'])
    copy(iotjs_output_path, nuttx_lib)


if opt_checktest():
    # do check test only when target is host.
    if opt_target_arch() == sys_machine() and opt_target_os() == sys_name():
        if not run_checktest():
            print_error("Failed run_checktest")
            sys.exit(1)
    else:
        print
        print "Skip run_checktest - target is not host"
        print


print
print "%sIoT.js Build Succeeded!!%s" % (TERM_GREEN, TERM_EMPTY)
print

sys.exit(0)
