/*@ requires \abs(\exact(x)) <= 0x1p-5;
    requires \round_error(x) <= 0x1p-20;
    ensures \abs(\exact(\result) - \cos(\exact(x))) <= 0x1p-24;
    ensures \round_error(\result) <= \round_error(x) + 0x20081p-41;
   */
float my_cosine2(float x) {
  float r = 1.0f - x * x * 0.5f;
  //@ assert \abs(\exact(r) - \cos(\exact(x))) <= 0x1p-24;
  return r;
}
