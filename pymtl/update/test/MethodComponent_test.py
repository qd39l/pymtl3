from pymtl import *

class Wire(MethodComponent):

  def __init__( s ):
    s.v = 0

    s.add_constraints(
      M(s.wr) < M(s.rd),
    )

  def wr( s, v ):
    s.v = v

  def rd( s ):
    return s.v

  def line_trace( s ):
    return "%d" % s.v

class Reg(MethodComponent):

  def __init__( s ):
    s.v1 = 0
    s.v2 = 0

    @s.update
    def up_reg():
      s.v2 = s.v1

    s.add_constraints(
      U(up_reg) < M(s.wr),
      M(s.rd)   > U(up_reg),
    )

  def wr( s, v ):
    s.v1 = v

  def rd( s ):
    return s.v2

  def line_trace( s ):
    return "[%d > %d]" % (s.v1, s.v2)

class RegWire(MethodComponent):

  def __init__( s ):
    s.v = 0

    s.add_constraints(
      M(s.rd) < M(s.wr),
    )

  def wr( s, v ):
    s.v = v

  def rd( s ):
    return s.v

  def line_trace( s ):
    return "%d" % s.v

def test_2regs_pure_method():

  class Top(MethodComponent):

    def __init__( s ):
      s.inc = 0
      s.in_ = Wire()

      @s.update
      def up_src():
        s.inc += 1
        s.in_.wr( s.inc )

      s.reg0 = RegWire()

      @s.update
      def up_plus_one_to_reg0():
        s.reg0.wr( s.in_.rd() + 1 )

      s.reg1 = Reg()

      @s.update
      def up_reg0_to_reg1():
        s.reg1.wr( s.reg0.rd() )

      s.out = 0
      @s.update
      def up_sink():
        s.out = s.reg1.rd()

    def line_trace( s ):
      return  s.in_.line_trace() + " >>> " + s.reg0.line_trace() + \
              " > " + s.reg1.line_trace() +\
              " >>> " + "out=%d" % s.out

  A = Top()
  A.elaborate()
  A.print_schedule()

  for x in xrange(1000000):
    A.cycle()

def test_2regs_mix():

  class Top(MethodComponent):

    def __init__( s ):
      s.in_ = 0

      @s.update
      def up_src():
        s.in_ += 1

      s.reg0 = RegWire()

      @s.update
      def up_plus_one_to_reg0():
        s.reg0.wr( s.in_ + 1 )

      s.reg1 = Reg()

      @s.update
      def up_reg0_to_reg1():
        s.reg1.wr( s.reg0.rd() )

      s.out = 0
      @s.update
      def up_sink():
        s.out = s.reg1.rd()

    def line_trace( s ):
      return  s.in_.line_trace() + " >>> " + s.reg0.line_trace() + \
              " > " + s.reg1.line_trace() +\
              " >>> " + "out=%d" % s.out

  A = Top()
  A.elaborate()
  A.print_schedule()

  for x in xrange(1000000):
    A.cycle()

def test_add_loopback_implicit():

  from pclib import TestSource
  from pclib import TestSink

  class Top(MethodComponent):

    def __init__( s ):

      s.src  = TestSource( [4,3,2,1] )
      s.sink = TestSink  ( ["?",(4+1),(3+1)+(4+1),(2+1)+(3+1)+(4+1),(1+1)+(2+1)+(3+1)+(4+1)] )

      s.reg0 = Reg()
      s.wire_back = 0

      @s.update
      def upA():
        tmp = s.src.out + 1
        s.reg0.wr( tmp + s.wire_back )

      @s.update
      def up_to_sink_and_loop_back():
        s.sink.in_  = s.wire_back = s.reg0.rd()

    def done( s ):
      return s.src.done() and s.sink.done()

    def line_trace( s ):
      return s.src.line_trace() + " >>> " + \
            "reg=%s > w_back=%s" % (s.reg0.line_trace(),s.wire_back) + \
             " >>> " + s.sink.line_trace()

  A = Top()
  A.elaborate()
  A.print_schedule()

  while not A.done():
    A.cycle()
    print A.line_trace()
