'''
Testing: pymol.creating
'''

from pymol import cmd, testing, stored

import unittest

class TestCreating(testing.PyMOLTestCase):

    def testGroup(self):
        cmd.pseudoatom('m1')
        cmd.pseudoatom('m2')
        cmd.pseudoatom('m3')
        m_list = []
        cmd.group('g1', 'm1 m2')
        cmd.iterate('g1', 'm_list.append(model)', space=locals())
        self.assertItemsEqual(m_list, ['m1', 'm2'])
        m_list = []
        cmd.ungroup('m2')
        cmd.iterate('g1', 'm_list.append(model)', space=locals())
        self.assertItemsEqual(m_list, ['m1'])

    def testUngroup(self):
        # see testGroup
        pass

    @unittest.skip("Not yet implemented.")
    def testIsomesh(self):
        pass

    @testing.requires('gui')
    def testVolume(self):
        cmd.fetch('1ubq', 'map', type='2fofc')
        cmd.volume('vol', 'map', '2fofc')
        x = cmd.get_volume_ramp('vol', 'sigma')
        y = [.9, 0., 0., 1., .0,
             1., 0., 0., 1., .2,
            1.4, 0., 0., 1., .0,]
        import numpy
        self.assertArrayEqual(x[5:-5], y, delta=0.1)
        cmd.set_volume_ramp('vol', 'esp')
        x = cmd.get_volume_ramp('vol', 'sigma')
        y = [-1., 1., 0., 0., .2,
             -.1, 1., 0., 0., .0,
              .1, 0., 0., 1., .0,
              1., 0., 0., 1., .2]
        self.assertArrayEqual(x[5:-5], y, delta=0.1)

    @unittest.skip("Not yet implemented.")
    def testIsosurface(self):
        pass

    @unittest.skip("Not yet implemented.")
    def testIsodot(self):
        pass

    @unittest.skip("Not yet implemented.")
    def testIsolevel(self):
        pass

    @unittest.skip("Not yet implemented.")
    def testGradient(self):
        pass

    def testCopy(self):
        cmd.fragment('ala', 'm1')
        cmd.copy('m2', 'm1')
        self.assertEqual(
                cmd.count_atoms('m1'),
                cmd.count_atoms('m2'))

    def testSymexp(self):
        cmd.load(self.datafile('1oky.pdb.gz'), 'm1')
        n = cmd.count_atoms()
        cmd.symexp('s', 'm1', '%m1 & resi 283', 20.0)
        x = cmd.get_object_list()
        self.assertEqual(x, [
            'm1',
            's01000000',
            's03000000',
            's04000000',
            ])
        self.assertEqual(n * 4, cmd.count_atoms())

    @unittest.skip("Not yet implemented.")
    def testFragment(self):
        pass

    def testCreate(self):
        cmd.fragment("ala")
        cmd.create("foo", "ala", 1, 1)

        names = cmd.get_names()
        names.sort()

        self.assertEquals(names, ["ala", "foo"])
        
        # TODO: Create a function to compare to chempy models
        # m1 = cmd.get_model("foo")
        # m2 = cmd.get_model("ala")
        # self.assertChempyModelEquals(m1, m2)

        self.assertEquals(cmd.fit("ala", "foo"), 0.0)

        self.assertEquals(cmd.count_states(), 1)

    def testCreateMultipleStates(self):
        cmd.fragment("ala")

        # simple creation

        self.assertEquals(cmd.count_states(), 1)

        cmd.create("foo", "ala", 1, 1)

        self.assertEquals(cmd.count_states(), 1)

        # creation into state 1

        cmd.create("foo", "ala", 1, 1)

        self.assertEquals(cmd.count_states(), 1)

        # creation into state 2

        cmd.create("foo", "ala", 1, 2)

        self.assertEquals(cmd.count_states(), 2)
        
    def create_many_states(self, fragment, obj, count):
        cmd.fragment(fragment)
        for x in range(count):
            cmd.create(obj, fragment, 1, count)

    def testCreateMany(self):

        # 10 states
        self.create_many_states("thr", "foo", 10)

        self.assertEquals(cmd.count_states("foo"), 10)
        self.assertEquals(cmd.count_states(), 10)

        # 100 states
        self.create_many_states("trp", "bar", 100)

        self.assertEquals(cmd.count_states("foo"), 10)
        self.assertEquals(cmd.count_states("bar"), 100)
        self.assertEquals(cmd.count_states(), 100)

        # 1000 states
        
        self.create_many_states("ile", "bam", 1000)

        self.assertEquals(cmd.count_states(), 1000)
        

    def testCreateLarge(self):
        pass

    def testCreateManyLarge(self):
        pass
        
    def testExtract(self):
        cmd.fragment('ala', 'm1')
        cmd.extract('m2', 'elem C')
        self.assertEqual(cmd.count_atoms('m1'), 7)
        self.assertEqual(cmd.count_atoms('m2'), 3)
    
    @unittest.skip("Not yet implemented.")
    def testUnquote(self):
        pass

    def testPseudoatom(self):
        cmd.set('retain_order')

        cmd.pseudoatom('m1', '', 'A1', 'B2', 1, 'D',
                'E5', 'F', 7.0, 0, 9.0, 0.1, '11', 'foo12',
                (13, 14, 15), 1)
        cmd.pseudoatom('m2', '', 'A1', 'B2', 2, 'A',
                'E5', 'F', 7.0, 0, 9.0, 0.1, '12', 'bar12',
                (13, 10, 15), 1)

        # append to m1, pos and vdw vom selection
        cmd.pseudoatom('m1', 'all', 'A2', 'B2', 3, 'D',
                'E5', 'F', -1, 1, 19.0, 0.2, '13', 'com12',
                None, 1, 'extent')

        r_list = []
        f_indices = [7, 9, 10, 13, 14, 15]

        cmd.iterate_state(1, 'all',
                'r_list.append([model, name, resn, resi, chain, segi, elem, '
                'vdw, type, b, q, color, label, x, y, z])', space=locals())

        for ref, values in zip(r_list, [
            ['m1', 'A1', 'B2', '1', 'D', 'E5', 'F', 7.0, 'ATOM', 9.0, 0.1, 11, 'foo12', 13.0, 14.0, 15.0],
            ['m1', 'A2', 'B2', '3', 'D', 'E5', 'F', 2.0, 'HETATM', 19.0, 0.2, 13, 'com12', 13.0, 12.0, 15.0],
            ['m2', 'A1', 'B2', '2', 'A', 'E5', 'F', 7.0, 'ATOM', 9.0, 0.1, 12, 'bar12', 13.0, 10.0, 15.0],
            ]):
            for i in f_indices:
                values[i] = round(values[i], 1)
                ref[i] = round(ref[i], 1)
            self.assertEqual(ref, values)

