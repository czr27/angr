import claripy
import logging

from ..java import JavaSimProcedure
from ...engines.soot.expressions import SimSootExpr_NewArray
from .collection import ELEMS, SIZE

log = logging.getLogger(name=__name__)


class ListInit(JavaSimProcedure):

    __provides__ = (
        ('java.util.List', '<init>()'),
        ('java.util.LinkedList', '<init>()')
    )

    def run(self, this_ref):
        log.debug('Called SimProcedure java.util.List.<init> with args: {}'.format(this_ref))

        array_ref = SimSootExpr_NewArray.new_array(self.state, 'java.lang.Object', claripy.BVV(1000, 32))
        this_ref.store_field(self.state, ELEMS, 'java.lang.Object[]', array_ref)
        this_ref.store_field(self.state, SIZE, 'int', claripy.BVV(0, 32))

        return


class ListAdd(JavaSimProcedure):

    __provides__ = (
        ('java.util.List', 'add(java.lang.Object)'),
        ('java.util.LinkedList', 'add(java.lang.Object)')
    )

    def run(self, this_ref, obj_ref):
        log.debug('Called SimProcedure java.util.List.add with args: {} {}'.format(this_ref, obj_ref))

        try:
            array_ref = this_ref.load_field(self.state, ELEMS, 'java.lang.Object[]')
        except KeyError:
            log.warning('{}.elems not found in memory during java.util.List.add'.format(this_ref))
            return claripy.BoolV(0)

        array_len = this_ref.load_field(self.state, SIZE, 'int')
        self.state.javavm_memory.store_array_element(array_ref, array_len, obj_ref)
        # Update size
        new_array_len = claripy.BVV(self.state.solver.eval(array_len) + 1, 32)
        this_ref.store_field(self.state, SIZE, 'int', new_array_len)

        return claripy.BoolV(1)


class ListGet(JavaSimProcedure):

    __provides__ = (
        ('java.util.List', 'get(int)'),
        ('java.util.LinkedList', 'get(int)')
    )

    def run(self, this_ref, index):
        log.debug('Called SimProcedure java.util.List.get with args: {} {}'.format(this_ref, index))

        array_ref = this_ref.load_field(self.state, ELEMS, 'java.lang.Object[]')
        array_len = this_ref.load_field(self.state, SIZE, 'int')
        # TODO should check boundaries?

        return self.state.javavm_memory.load_array_element(array_ref, index)


class ListGetFirst(JavaSimProcedure):

    __provides__ = (
        ('java.util.LinkedList', 'getFirst()'),
    )

    def run(self, this_ref):
        log.debug('Called SimProcedure java.util.List.getFirst with args: {}'.format(this_ref))

        array_ref = this_ref.load_field(self.state, ELEMS, 'java.lang.Object[]')
        array_len = this_ref.load_field(self.state, SIZE, 'int')

        # TODO should check boundaries?

        return self.state.javavm_memory.load_array_element(array_ref, claripy.BVV(0, 32))


class ListSize(JavaSimProcedure):

    __provides__ = (
        ('java.util.List', 'size()'),
        ('java.util.LinkedList', 'size()')
    )

    def run(self, this_ref):
        log.debug('Called SimProcedure java.util.List.size with args: {}'.format(this_ref))

        try:
            return this_ref.load_field(self.state, SIZE, 'int')
        except KeyError:
            log.warning('{}.size not found in memory during java.util.List.size'.format(this_ref),
                        'Returning a symbolic value')
            return claripy.BVS('list_size', 32)

