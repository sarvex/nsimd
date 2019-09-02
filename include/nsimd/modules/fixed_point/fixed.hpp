/*

Copyright (c) 2019 Agenium Scale

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

*/

#ifndef NSIMD_MODULES_FIXED_POINT_FIXED_HPP
#define NSIMD_MODULES_FIXED_POINT_FIXED_HPP

#include <iostream>
#include <limits>
#include <stdint.h>
// #include <type_traits>

#include <nsimd/nsimd.h>

namespace nsimd {
namespace fixed_point {
// Convert generic integer to fixed point decimal
template <uint8_t lf, uint8_t rt, typename Out_Type, typename In_Type>
void integer_convert(Out_Type &out, const In_Type &in) {
  const uint8_t extra = 8 * sizeof(Out_Type) - lf - rt;
  const uint8_t shift = rt + extra;
  out = In_Type(in) << shift;

  return;
}

template <uint8_t lf, uint8_t rt, typename Out_Type, typename In_Type>
void int2fixed(Out_Type &out, const In_Type &in) {
  integer_convert<lf, rt>(out, in);
}

// Convert generic float to fixed point decimal
template <typename Out_Type, // Output - raw int_xx type
          typename In_Type,  // Input  - float/double with associated format in
                             // arguments
          typename Max_UInt, // Unsigned int with same size as In_Type
          uint8_t lf, uint8_t rt, uint8_t b_exp, // IEEE defined exponent
          uint16_t m_exp                         // IEEE defined exponent bias
          >
void generic_convert(Out_Type &out, const In_Type &in);

template <typename Out_Type, typename In_Type, uint8_t lf, uint8_t rt>
void easy_convert(Out_Type &out, const In_Type &in);

template <typename Out_Type, uint8_t lf, uint8_t rt>
void float2fixed(Out_Type &out, const double &in) {
  easy_convert<Out_Type, double, lf, rt>(out, in);
}

template <typename Out_Type, uint8_t lf, uint8_t rt>
void float2fixed(Out_Type &out, const float &in) {
  easy_convert<Out_Type, float, lf, rt>(out, in);
}

template <typename Out_Type, typename In_Type, uint8_t lf, uint8_t rt>
void easy_convert(Out_Type &out, const In_Type &in) {
  const Out_Type extra = 8 * sizeof(Out_Type) - lf - rt;
  const Out_Type out_one = 1 << (rt + extra);
  In_Type tmp = in * out_one;
  out = Out_Type(tmp);

  return;
}

template <uint8_t _lf, uint8_t _rt> struct fp_t;

template <uint8_t _lf, uint8_t _rt> float fixed2float(const fp_t<_lf, _rt> &in);

//------------------------------------------------------------------------------
// Helper class to outsource the _raw size evaluation
//------------------------------------------------------------------------------

template <bool B, typename T = void> struct enable_if {};

template <typename T> struct enable_if<true, T> { typedef T type; };

template <uint8_t _lf, uint8_t _rt, typename T = void> struct fp_types {};

//  1-8 total bits = char
template <uint8_t _lf, uint8_t _rt>
struct fp_types<
    _lf, _rt,
    typename enable_if<(((_lf + _rt) > 0)) && ((_lf + _rt) <= 8)>::type> {
  typedef int8_t value_type;
  typedef int16_t value_up;
  typedef int8_t logical_type;
  typedef vi8 simd_type;
  typedef vi16 simd_up;
  typedef vli8 simd_logical;
};

//  9-16 total bits = char
template <uint8_t _lf, uint8_t _rt>
struct fp_types<
    _lf, _rt,
    typename enable_if<(((_lf + _rt) > 8)) && ((_lf + _rt) <= 16)>::type> {
  typedef int16_t value_type;
  typedef int32_t value_up;
  typedef int16_t logical_type;
  typedef vi16 simd_type;
  typedef vi32 simd_up;
  typedef vli16 simd_logical;
};

//  17-32 total bits = char
template <uint8_t _lf, uint8_t _rt>
struct fp_types<
    _lf, _rt,
    typename enable_if<(((_lf + _rt) > 16)) && ((_lf + _rt) <= 32)>::type> {
  typedef int32_t value_type;
  typedef int64_t value_up;
  typedef int32_t logical_type;
  typedef vi32 simd_type;
  typedef vi64 simd_up;
  typedef vli32 simd_logical;
};

//------------------------------------------------------------------------------
// Generic template declaration
// _lf represents the number of bits before the decimal (INCLUDING the sign bit)
// _rt represents the number of bits after the decimal
// Functionality assumes that the numbers are stored with extra bits to the
// right.
//   As far as math functionalities are concerned, right or left is equivalent,
//   but extra bits on the right makes it easier to take advantage of integer
//   math
// SIGNED integers means the front can hold up to (2**(_lf-2) - 1)
//------------------------------------------------------------------------------

template <uint8_t _lf, uint8_t _rt> struct fp_t {
  static const uint8_t lf = _lf;
  static const uint8_t rt = _rt;
  typedef typename fp_types<_lf, _rt>::value_type value_type;
  typedef typename fp_types<_lf, _rt>::logical_type logical_type;
  typedef typename fp_types<_lf, _rt>::value_up value_up;
  typedef typename fp_types<_lf, _rt>::simd_type simd_type;
  typedef typename fp_types<_lf, _rt>::simd_up simd_up;
  typedef typename fp_types<_lf, _rt>::simd_logical simd_logical;
  value_type _raw;

  fp_t() {}

  fp_t(const fp_t<_lf, _rt> &cp) { _raw = cp._raw; }

  inline fp_t(const float &in) { float2fixed<value_type, _lf, _rt>(_raw, in); }

  inline fp_t(const double &in) { float2fixed<value_type, _lf, _rt>(_raw, in); }

  template <typename T> fp_t(const T &in) {
    integer_convert<_lf, _rt>(_raw, in);
  }

  fp_t &operator=(const fp_t<_lf, _rt> &cp) {
    _raw = cp._raw;
    return *this;
  }

  fp_t &operator+=(const fp_t<_lf, _rt> &pl) {
    *this = *this + pl;
    return *this;
  }

  fp_t &operator-=(const fp_t<_lf, _rt> &mi) {
    *this = *this - mi;
    return *this;
  }

  fp_t &operator*=(const fp_t<_lf, _rt> &ti) {
    *this = *this * ti;
    return *this;
  }

  fp_t &operator/=(const fp_t<_lf, _rt> &di) {
    *this = *this / di;
    return *this;
  }

  template <typename T> operator T() const {
    return T(fixed2float<_lf, _rt>(*this));
  }
};

//------------------------------------------------------------------------------
// For examining available precision
//------------------------------------------------------------------------------
template <uint8_t _lf, uint8_t _rt> uint8_t left(const fp_t<_lf, _rt>) {
  return _lf;
}

template <uint8_t _lf, uint8_t _rt> uint8_t right(const fp_t<_lf, _rt>) {
  return _rt;
}

//------------------------------------------------------------------------------
// Display function
//------------------------------------------------------------------------------
template <uint8_t _lf, uint8_t _rt>
float fixed2float(const fp_t<_lf, _rt> &in) {
  typedef typename fp_t<_lf, _rt>::value_type fx_t;

  // Remove any extra leading bits
  const uint8_t total = _lf + _rt;
  const uint8_t extra = 8 * sizeof(fx_t) - total;
  fx_t mask_lf = 0;
  uint64_t exp = 1;
  for (int i = 0; i < extra; ++i) {
    mask_lf += exp;
    exp *= 2;
  }
  mask_lf = ~mask_lf;
  fx_t trunc_in = (in._raw & mask_lf);
  // ns::print_bits( trunc_in );

  // Divide by correct power of 2
  exp = 1;
  for (int i = 0; i < _rt; ++i) {
    exp *= 2;
  }
  for (int i = 0; i < extra; ++i) {
    exp *= 2;
  }
  float val = float(trunc_in) / exp;

  return val;
}

template <uint8_t _lf, uint8_t _rt>
std::ostream &operator<<(std::ostream &stream, const fp_t<_lf, _rt> &in) {
  stream << fixed2float(in);

  return stream;
}

} // namespace fixed_point
} // namespace nsimd

#endif
