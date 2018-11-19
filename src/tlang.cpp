#include "tlang.h"
#include <taichi/common/task.h>

TC_NAMESPACE_BEGIN

// if branching is not supported

using namespace Tlang;
template <typename T>
Expr compile(int dim) {
  Expr a[dim][dim], b[dim][dim], c[dim][dim];

  int simd_width = 32 / sizeof(float32);

  for (int i = 0; i < dim; i++) {
    for (int j = 0; j < dim; j++) {
      a[i][j] = load(0, simd_width * dim * dim, simd_width * (i * dim + j));
      b[i][j] = load(1, simd_width * dim * dim, simd_width * (i * dim + j));
    }
  }

  Expr ret;
  for (int i = 0; i < dim; i++) {
    for (int j = 0; j < dim; j++) {
      auto sum = a[i][0] * b[0][j];
      for (int k = 1; k < dim; k++) {
        sum = sum + a[i][k] * a[k][j];
      }
      ret.store(sum, 2, simd_width * dim * dim, simd_width * (i * dim + j));
    }
  }
  return ret;
}

auto tlang = []() {
  auto expr = compile<float32>(3);
  CodeGen cg;
  auto func = cg.get(expr);
  TC_P(func);
};

TC_REGISTER_TASK(tlang);

TC_NAMESPACE_END

// ti run tlang && g++ tmp.cpp -std=c++14 -c -fPIC -o tmp.so -march=native