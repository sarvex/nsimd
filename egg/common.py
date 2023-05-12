# Use utf-8 encoding
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Agenium Scale
#
# permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------

# What does this script?
# ----------------------
#
# This is only a python module that holds what is shared by `generate.py`,
# the `platform_*.py` files and all other python code in `egg`. If contains
# the list of supported types, functions, operators, and some useful helper
# functions such as the python equivalent of `mkdir -p`.

# -----------------------------------------------------------------------------
# Import section

import math
import os
import sys
import io
import collections
import platform
import string
import shutil
import math

# -----------------------------------------------------------------------------
# print

def myprint(opts, obj):
    if opts.list_files:
        return
    print(f'-- {obj}')

# -----------------------------------------------------------------------------
# check if file exists

def can_create_filename(opts, filename):
    if opts.list_files:
        print(filename)
        return False
    if opts.verbose:
        sys.stdout.write(f'-- {filename}: ')
    if os.path.isfile(filename) and not opts.force:
        if opts.verbose:
            sys.stdout.write('skipping\n')
        return False
    elif opts.force:
        if opts.verbose:
            sys.stdout.write('creating (forced)\n')
        return True
    else:
        if opts.verbose:
            sys.stdout.write('creating (missing)\n')
        return True

# -----------------------------------------------------------------------------
# open with UTF8 encoding

def open_utf8(opts, filename):
    dummy, ext = os.path.splitext(filename)
    if ext.lower() in ['.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hxx',
                       '.hpp']:
        begin_comment = '/*'
        end_comment = '*/'
    elif ext.lower() in ['.md', '.htm', '.html']:
        begin_comment = '<!--'
        end_comment = '-->'
    else:
        begin_comment = None
    with io.open(filename, mode='w', encoding='utf-8') as fout:
        if begin_comment is not None:
            if opts.simple_license:
                fout.write('''{}

Copyright (c) 2021 Agenium Scale

{}

'''.format(begin_comment, end_comment))
            else:
                fout.write('''{}

Copyright (c) 2021 Agenium Scale

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

{}

'''.format(begin_comment, end_comment))

        fout.write(
            f'{begin_comment} This file has been auto-generated {end_comment}\n\n'
        )

    return io.open(filename, mode='a', encoding='utf-8')

# -----------------------------------------------------------------------------
# clang-format

def clang_format(opts, filename, cuda=False):
    with io.open(filename, 'a', encoding='utf-8') as fout:
        fout.write('\n')
    if not opts.enable_clang_format:
        if cuda:
            os.system('clang-format -style="{{ Standard: Cpp11 }}" -i {}'. \
                      format(filename))
        else:
            os.system('clang-format -style="{{ Standard: Cpp03 }}" -i {}'. \
                      format(filename))
    if cuda:
        shutil.copyfile(filename, f'{filename[:-4]}.cu')

# -----------------------------------------------------------------------------
# Not implemented response

NOT_IMPLEMENTED = 'abort();'

# -----------------------------------------------------------------------------
# C/C++ comment hbar

hbar = '/* ' + ('-' * 73) + ' */'

# -----------------------------------------------------------------------------
# Convert constants for operators

OUTPUT_TO_SAME_TYPE       = 0
OUTPUT_TO_SAME_SIZE_TYPES = 1
OUTPUT_TO_UP_TYPES        = 2
OUTPUT_TO_DOWN_TYPES      = 3

# -----------------------------------------------------------------------------
# SIMD type

x86_simds = [
    'sse2',
    'sse42',
    'avx',
    'avx2',
    'avx512_knl',
    'avx512_skylake',
]

arm_simds = [
    'neon128',
    'aarch64',
    'sve',
    'sve128',
    'sve256',
    'sve512',
    'sve1024',
    'sve2048'
]

ppc_simds = [
    'vmx',
    'vsx',
]

simds = ['cpu'] + x86_simds + arm_simds + ppc_simds

simds_deps = {
    'cpu': ['cpu'],
    'sse2': ['cpu', 'sse2'],
    'sse42': ['cpu', 'sse2', 'sse42'],
    'avx': ['cpu', 'sse2', 'sse42', 'avx'],
    'avx2': ['cpu', 'sse2', 'sse42', 'avx', 'avx2'],
    'fma4': [],
    'avx512_knl': ['cpu', 'sse2', 'sse42', 'avx', 'avx2', 'avx512_knl'],
    'avx512_skylake': ['cpu', 'sse2', 'sse42', 'avx', 'avx2', 'avx512_skylake'],
    'neon128': ['cpu', 'neon128'],
    'aarch64': ['cpu', 'aarch64'],
    'sve': ['cpu', 'aarch64', 'sve'],
    'sve128': ['cpu', 'aarch64', 'sve128'],
    'sve256': ['cpu', 'aarch64', 'sve256'],
    'sve512': ['cpu', 'aarch64', 'sve512'],
    'sve1024': ['cpu', 'aarch64', 'sve1024'],
    'sve2048': ['cpu', 'aarch64', 'sve2048'],
    'vmx': ['cpu', 'vmx'],
    'vsx': ['cpu', 'vmx', 'vsx']
}

ftypes = ['f64', 'f32', 'f16']
ftypes_no_f16 = ['f64', 'f32']
itypes = ['i64', 'i32', 'i16', 'i8']
utypes = ['u64', 'u32', 'u16', 'u8']
iutypes = itypes + utypes
types = ftypes + iutypes

def logical(typ):
    return f'l{typ}'

signed_type = {
    'i8': 'i8',
    'u8': 'i8',
    'i16': 'i16',
    'u16': 'i16',
    'i32': 'i32',
    'u32': 'i32',
    'i64': 'i64',
    'u64': 'i64',
    'f16': 'f16',
    'f32': 'f32',
    'f64': 'f64'
}

bitfield_type = {
    'i8': 'u8',
    'u8': 'u8',
    'i16': 'u16',
    'u16': 'u16',
    'i32': 'u32',
    'u32': 'u32',
    'i64': 'u64',
    'u64': 'u64',
    'f16': 'u16',
    'f32': 'u32',
    'f64': 'u64'
}

in0 = 'a0'
in1 = 'a1'
in2 = 'a2'
in3 = 'a3'
in4 = 'a4'
in5 = 'a5'

CPU_NBITS = 128

if CPU_NBITS != 128:
    raise ValueError('CPU_NBITS must be 128')

def get_arg(i):
    fmtspec = { 'in0': in0, 'in1': in1, 'in2': in2, 'in3': in3, 'in4': in4,
                'in5': in5 }
    return '{{in{}}}'.format(i).format(**fmtspec)

def get_args(n):
    fmtspec = { 'in0': in0, 'in1': in1, 'in2': in2, 'in3': in3, 'in4': in4,
                'in5': in5 }
    return ', '.join(['{{in{}}}'.format(i).format(**fmtspec) \
                      for i in range(0, n)])

def get_simds_deps_from_opts(opts):
    simds = set()
    for simd1 in opts.simd:
        for simd2 in simds_deps[simd1]:
            simds.add(simd2)
    return simds

def bitsize(typ):
    if typ not in types:
        raise ValueError(f'Unknown type "{typ}"')
    return int(typ[1:])

def sizeof(typ):
    return bitsize(typ) // 8

def ilog2(x):
    if x <= 0:
        return None
    for i in range(0, x):
        if 2 ** (i + 1) > x:
            return i

#def get_same_size_types(typ):
#    nbits = typ[1:]
#    if typ in ['i8' ,'u8']:
#        return ['i8', 'u8']
#    else:
#        return ['i' + nbits, 'u' + nbits, 'f' + nbits]

def get_output_types(from_typ, output_to):
    if output_to == OUTPUT_TO_SAME_TYPE:
        return [from_typ]
    nbits = from_typ[1:]
    if output_to == OUTPUT_TO_SAME_SIZE_TYPES:
        return (
            ['i8', 'u8']
            if from_typ in ['i8', 'u8']
            else [f'i{nbits}', f'u{nbits}', f'f{nbits}']
        )
    elif output_to == OUTPUT_TO_UP_TYPES:
        if nbits == '64':
            raise ValueError(f'No uptype for {from_typ}')
        n = str(int(nbits) * 2)
        return [f'i{n}', f'u{n}', f'f{n}']
    elif output_to == OUTPUT_TO_DOWN_TYPES:
        n = str(int(nbits) // 2)
        if nbits == '16':
            return [f'i{n}', f'u{n}']
        elif nbits == '8':
            raise ValueError(f'No downtype for {from_typ}')
        else:
            return [f'i{n}', f'u{n}', f'f{n}']
    else:
        raise ValueError(f'Invalid argument for "output_to": {output_to}')

# -----------------------------------------------------------------------------
# mkdir -p (avoid a dependency for just one function)

def mkdir_p(path):
    if os.path.isdir(path):
        return path
    head, tail = os.path.split(path)
    if head != '':
        mkdir_p(head)
    os.mkdir(path)
    return path

# -----------------------------------------------------------------------------
# Replacement of enumerate

def enum(l):
    return [[i, l[i]] for i in range(0, len(l))]

# -----------------------------------------------------------------------------
# List of supported SIMD operators/functions

# v   = SIMD vector parameter
# vi  = SIMD vector of signed integers parameter
# vx2 = struct of 2 SIMD vector parameters
# vx3 = struct of 3 SIMD vector parameters
# vx4 = struct of 4 SIMD vector parameters
# l   = SIMD vector of logicals parameter
# s   = Scalar parameter
# *   = Pointer to scalar parameter
# c*  = Pointer to const scalar parameter
# _   = void (only for return type)
# p   = Parameter (int)


# -----------------------------------------------------------------------------
# Type generators

def get_one_type_generic(param, typ):
    if param == '_':
        return 'void'
    elif param == 'p':
        return 'int'
    elif param == 's':
        return typ
    elif param == '*':
        return f'{typ}*'
    elif param == 'c*':
        return f'{typ} const*'
    elif param == 'vi':
        return f'vi{typ[1:]}'
    elif param == 'v':
        return f'v{typ}'
    elif param == 'vx2':
        return f'v{typ}x2'
    elif param == 'vx3':
        return f'v{typ}x3'
    elif param == 'vx4':
        return f'v{typ}x4'
    elif param == 'l':
        return f'vl{typ}'
    else:
        raise ValueError(f"Unknown param '{param}'")

def get_one_type_specific(param, ext, typ):
    if param == '_':
        return 'void'
    elif param == 'p':
        return 'int'
    elif param == 's':
        return typ
    elif param == '*':
        return f'{typ}*'
    elif param == 'c*':
        return f'{typ} const*'
    elif param == 'vi':
        return f'nsimd_{ext}_vi{typ[1:]}'
    elif param == 'v':
        return f'nsimd_{ext}_v{typ}'
    elif param == 'vx2':
        return f'nsimd_{ext}_v{typ}x2'
    elif param == 'vx3':
        return f'nsimd_{ext}_v{typ}x3'
    elif param == 'vx4':
        return f'nsimd_{ext}_v{typ}x4'
    elif param == 'l':
        return f'nsimd_{ext}_vl{typ}'
    else:
        raise ValueError(f"Unknown param '{param}'")

def get_one_type_pack(param, inout, N):
    if param == '_':
        return 'void'
    if param == 'p':
        return 'int'
    if param == '*':
        return 'T*'
    if param == 'c*':
        return 'T const*'
    if param == 's':
        return 'T'
    if param in ['v', 'vx2', 'vx3', 'vx4']:
        if inout == 0:
            return f'pack<T, {N}, SimdExt> const&'
        else:
            return f'pack<T, {N}, SimdExt>'
    if param == 'l':
        return (
            f'packl<T, {N}, SimdExt> const&'
            if inout == 0
            else f'packl<T, {N}, SimdExt>'
        )
    elif param == 'vi':
        return (
            f'pack<typename traits<T>::itype, {N}, SimdExt> const&'
            if inout == 0
            else f'pack<typename traits<T>::itype, {N}, SimdExt>'
        )
    raise ValueError(f"Unknown param '{param}'")

def get_one_type_generic_adv_cxx(param, T, N):
    if param == '_':
        return 'void'
    elif param == 'p':
        return 'int'
    elif param == '*':
        return f'{T}*'
    elif param == 'c*':
        return f'{T} const*'
    elif param == 's':
        return T
    elif param == 'v':
        return f'pack<{T}, {N}, SimdExt>'
    elif param == 'vi':
        return f'pack<i{T[1:]}, {N}, SimdExt>'
    elif param == 'vx2':
        return f'packx2<{T}, {N}, SimdExt>'
    elif param == 'vx3':
        return f'packx3<{T}, {N}, SimdExt>'
    elif param == 'vx4':
        return f'packx4<{T}, {N}, SimdExt>'
    elif param == 'l':
        return f'packl<{T}, {N}, SimdExt>'
    else:
        raise ValueError(f'Unknown param: "{param}"')

def get_one_type_scalar(param, t):
    if param == '_':
        return 'void'
    elif param in ['p', 'l']:
        return 'int'
    elif param in ['s', 'v']:
        return t
    else:
        raise ValueError(f'Unknown param: "{param}"')

def get_first_discriminating_type(params):
    return next(
        (
            i
            for i in range(len(params))
            if params[i] in ['v', 'l', 'vx2', 'vx3', 'vx4']
        ),
        -1,
    )

# -----------------------------------------------------------------------------
# Formats

def pprint_lines(what):
    return '\n'.join(what)

def pprint_commas(what):
    return ', '.join(what)

def pprint_includes(what):
    return pprint_lines(f'#include {i}' for i in what)

# -----------------------------------------------------------------------------
# Function parsing signatures

def parse_signature(signature):
    l = signature.split(' ');
    name = l[1]
    params = [l[0]] + l[2:] if len(l) > 2 else [l[0]]
    return (name, params)

# -----------------------------------------------------------------------------
# Load platforms

def get_platforms(opts):
    if opts.platforms_list != None:
        return opts.platforms_list
    ret = {}
    path = opts.script_dir
    myprint(opts, f'Searching platforms in "{path}"')
    for mod_file in os.listdir(path):
        if mod_file[-3:] == '.py' and mod_file[:9] == 'platform_':
            mod_name = mod_file[:-3]
            myprint(opts, f'Found new platform: {mod_name[9:]}')
            ret[mod_name[9:]] = __import__(mod_name)
    opts.platforms_list = ret
    return ret

# -----------------------------------------------------------------------------
# Find modules

def get_modules(opts):
    if opts.modules_list != None:
        return opts.modules_list
    ret = {}
    # We have one module by directory
    path = os.path.join(opts.script_dir, 'modules')
    myprint(opts, f'Searching modules in "{path}"')
    for module_dir in os.listdir(path):
        if (not os.path.isdir(os.path.join(path, module_dir))) or \
           module_dir == '.' or module_dir == '..' or \
           (not os.path.exists(os.path.join(path, module_dir, 'hatch.py'))):
            continue
        myprint(opts, f'Found new module: {module_dir}')
        mod = __import__(f'modules.{module_dir}.hatch')
        ret[module_dir] = mod
    opts.modules_list = ret
    return ret

# -----------------------------------------------------------------------------
# Integer limits per type using macros defined in <limits.h> or <climits>

limits = {
    'i8':   {'min': 'NSIMD_I8_MIN',     'max': 'NSIMD_I8_MAX'   },
    'i16':  {'min': 'NSIMD_I16_MIN',    'max': 'NSIMD_I16_MAX'  },
    'i32':  {'min': 'NSIMD_I32_MIN',    'max': 'NSIMD_I32_MAX'  },
    'i64':  {'min': 'NSIMD_I64_MIN',    'max': 'NSIMD_I64_MAX'  },
    'u8':   {'min': 'NSIMD_U8_MIN',     'max': 'NSIMD_U8_MAX'   },
    'u16':  {'min': 'NSIMD_U16_MIN',    'max': 'NSIMD_U16_MAX'  },
    'u32':  {'min': 'NSIMD_U32_MIN',    'max': 'NSIMD_U32_MAX'  },
    'u64':  {'min': 'NSIMD_U64_MIN',    'max': 'NSIMD_U64_MAX'  }
  }

# -----------------------------------------------------------------------------
# Misc

def ext_from_lang(lang):
    return 'c' if lang == 'c_base' else 'cpp'

def nsimd_category(category):
    return f'nsimd_{category}'

# ------------------------------------------------------------------------------
# Doc common

def to_filename(op_name):
    valid = string.ascii_letters + string.digits
    return ''.join('-' if c not in valid else c for c in op_name)

def get_markdown_dir(opts):
    return os.path.join(opts.script_dir, '..', 'doc', 'markdown')

def get_markdown_api_file(opts, name, module=''):
    root = get_markdown_dir(opts)
    op_name = to_filename(name)
    if module == '':
        return os.path.join(root, f'api_{op_name}.md')
    else:
        return os.path.join(root, f'module_{module}_api_{op_name}.md')

def get_markdown_file(opts, name, module=''):
    root =  get_markdown_dir(opts)
    op_name = to_filename(name)
    if module == '':
        return os.path.join(root, f'{op_name}.md')
    else:
        return os.path.join(root, f'module_{module}_{op_name}.md')

