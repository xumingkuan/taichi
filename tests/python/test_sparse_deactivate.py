import taichi as ti


@ti.archs_support_sparse
def test_pointer():
  x = ti.var(ti.f32)
  s = ti.var(ti.i32)

  n = 16

  @ti.layout
  def place():
    ti.root.dense(ti.i, n).pointer().dense(ti.i, n).place(x)
    ti.root.place(s)

  s[None] = 0

  @ti.kernel
  def func():
    for i in x:
      s[None] += 1


  x[0] = 1
  x[19] = 1
  func()
  assert s[None] == 32

  @ti.kernel
  def deactivate():
    ti.deactivate(x.parent().parent(), 4)

  deactivate()
  s[None] = 0
  func()
  assert s[None] == 16

@ti.archs_support_sparse
def test_pointer2():
  x = ti.var(ti.f32)

  n = 16

  @ti.layout
  def place():
    ti.root.dense(ti.i, n).pointer().dense(ti.i, n).place(x)

  @ti.kernel
  def func():
    for i in range(n*n):
      x[i] = 1.0

  @ti.kernel
  def set10():
    x[10] = 10.0

  @ti.kernel
  def clear():
    for i in x.parent().parent():
      ti.deactivate(x.parent().parent(),i)

  func()
  clear()

  for i in range(n * n):
    assert x[i] == 0.0

  set10()

  for i in range(n*n):
    if i != 10:
      assert x[i] == 0.0
    else:
      assert x[i] == 10.0

@ti.archs_support_sparse
def test_pointer3():
  x = ti.var(ti.f32)
  x_temp = ti.var(ti.f32)

  n = 16

  @ti.layout
  def place():
    ti.root.dense(ti.ij, n).pointer().dense(ti.ij, n).place(x)
    ti.root.dense(ti.ij, n).pointer().dense(ti.ij, n).place(x_temp)

  @ti.kernel
  def fill():
    for j in range(n*n):
      for i in range(n*n):
        x[i,j] = i+j

  @ti.kernel
  def fill2():
    for i,j in x_temp:
      if x_temp[i,j] < 100:
        x[i,j] = x_temp[i,j]

  @ti.kernel
  def copy_to_temp():
    for i,j in x:
      x_temp[i,j] = x[i,j]

  @ti.kernel
  def copy_from_temp():
    for i,j in x_temp:
      x[i,j] = x_temp[i,j]

  @ti.kernel
  def clear():
    for i,j in x.parent().parent():
      ti.deactivate(x.parent().parent(),[i,j])

  @ti.kernel
  def clear_temp():
    for i,j in x_temp.parent().parent():
      ti.deactivate(x_temp.parent().parent(),[i,j])

  fill()
  copy_to_temp()
  clear()
  fill2()
  clear_temp()


  for iter in range(100):
    print(iter)
    copy_to_temp()
    clear()
    copy_from_temp()
    clear_temp()

    for j in range(n * n):
      for i in range(n * n):
        if i+j < 100:
          assert x[i,j] == i+j



@ti.archs_support_sparse
def test_dynamic():
  x = ti.var(ti.i32)
  s = ti.var(ti.i32)

  n = 16

  @ti.layout
  def place():
    ti.root.dense(ti.i, n).dynamic(ti.j, 4096).place(x)
    ti.root.dense(ti.i, n).place(s)

  @ti.kernel
  def func(mul: ti.i32):
    for i in range(n):
      for j in range(i * i * mul):
        ti.append(x.parent(), i, j)
      s[i] = ti.length(x.parent(), i)


  func(1)

  for i in range(n):
    assert s[i] == i * i

  @ti.kernel
  def clear():
    for i in range(n):
      ti.deactivate(x.parent(), i)

  func(2)

  for i in range(n):
    assert s[i] == i * i * 3

  clear()
  func(4)

  for i in range(n):
    assert s[i] == i * i * 4
