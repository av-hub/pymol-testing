'''
Testing: pymol.editing
'''

from pymol import cmd, testing, stored

def get_coord_list(selection, state=1):
    return cmd.get_model(selection, state).get_coord_list()

class TestEditing(testing.PyMOLTestCase):

    alter_names_atomic = {
        str: ('segi', 'chain', 'resn', 'resi', 'name', 'alt', 'elem', 'text_type'),
        int: ('formal_charge', 'numeric_type', 'ID'),
        float: ('q', 'b', 'partial_charge', 'vdw'),
    }

    alter_names_atomic_special = {
        str: ('model', 'type'),
        int: ('resv',),
    }

    alter_names_state = {
        float: ('x', 'y', 'z'),
    }

    def testIterate(self):
        cmd.pseudoatom('m1')

        for ptype, names in (
                self.alter_names_atomic.items() +
                self.alter_names_atomic_special.items()):
            stored.v_names = None
            cmd.iterate('all', 'stored.v_names = [' + ','.join(names) + ']')

            self.assertNotEqual(stored.v_names, None)
            for v in stored.v_names:
                self.assertTrue(isinstance(v, ptype))

    @testing.foreach(cmd.iterate, cmd.alter)
    def testIterateLocalVars(self, func):
        cmd.pseudoatom('m1')
        stored.v = None
        func('all', 'foobar = model;stored.v = foobar')
        self.assertEqual(stored.v, 'm1')

    def testIterateState(self):
        cmd.fragment('ala')
        cmd.create('ala', 'ala', 1, 2)
        self.assertEqual(2, cmd.count_states())

        v_count = cmd.count_atoms('all')
        expr = 'v_xyz.append(((model,index), (x,y,z)))'

        # current state
        v_xyz = []
        cmd.iterate_state(-1, 'all', expr, space=locals())
        self.assertEqual(len(v_xyz), v_count)

        # all states
        v_xyz = []
        cmd.iterate_state(0, 'all', expr, space=locals())
        self.assertEqual(len(v_xyz), v_count * 2)

        # atomic=0
        stored.v_xyz = []
        cmd.iterate_state(1, 'all', 'stored.v_xyz.append((x,y,z))', atomic=0)
        self.assertEqual(len(stored.v_xyz), v_count)

        space = {'self': self, 'NameError': NameError, 'v_list': []}
        cmd.iterate_state(1, 'all',
                'v_list.append(self.assertRaises(NameError, lambda: (model, index)))',
                space=space)
        self.assertEqual(len(space['v_list']), v_count)

    def testAlter(self):
        cmd.pseudoatom('m1')

        for ptype, names in self.alter_names_atomic.items():
            stored.v_mock = tuple(map(ptype, range(len(names))))
            names_fmt = '(' + ','.join(names) + ',)'

            if not (cmd.alter('all', names_fmt + ' = stored.v_mock') and
                    cmd.iterate('all', 'stored.v_names = ' + names_fmt)):
                raise UserWarning('iterate failed')

            self.assertEqual(stored.v_names, stored.v_mock)

    def testAlterState(self):
        cmd.fragment('ala')
        cmd.create('ala', 'ala', 1, 2)
        v_count = cmd.count_atoms('all')

        v_mock = [map(float, range(i*3, (i+1)*3)) for i in range(v_count)]

        v_xyz_1_pre = cmd.get_model('all', state=1).get_coord_list()
        v_xyz_2_pre = cmd.get_model('all', state=2).get_coord_list()

        cmd.alter_state(2, 'all', '(x,y,z) = xyz_iter.next()',
                space={'xyz_iter': iter(v_mock)})

        v_xyz_1_post = cmd.get_model('all', state=1).get_coord_list()
        v_xyz_2_post = cmd.get_model('all', state=2).get_coord_list()

        self.assertEqual(v_xyz_1_post, v_xyz_1_pre)
        self.assertEqual(v_xyz_2_post, v_mock)

    def test_alter_list(self):
        cmd.fragment('gly')
        cmd.alter_list('gly', [[i+1, 'name = "X%d"' % i] for i in range(7)])
        name_list = []
        cmd.iterate('gly', 'name_list.append(name)', space=locals())
        self.assertEqual(name_list, ['X%d' % i for i in range(7)])

    def test_attach(self):
        cmd.pseudoatom()
        cmd.edit('first all')
        cmd.attach('C', 1, 1)
        self.assertEqual(2, cmd.count_atoms())

    def test_bond(self):
        cmd.pseudoatom('m1', pos=(0,0,0))
        cmd.pseudoatom('m1', pos=(1,0,0))
        cmd.pseudoatom('m1', pos=(1,1,0))

        cmd.bond('m1`1', 'm1`2')
        count = cmd.count_atoms('(m1`1) extend 1')
        self.assertEqual(count, 2)

        cmd.unbond('m1`1', 'm1`2')
        count = cmd.count_atoms('(m1`1) extend 1')
        self.assertEqual(count, 1)

    def test_cycle_valence(self):
        cmd.fragment('gly')
        cmd.edit('ID 0', 'ID 1')

        cmd.cycle_valence()
        self.assertEqual(4, cmd.get_model('pkbond').bond[0].order)

        cmd.cycle_valence()
        self.assertEqual(2, cmd.get_model('pkbond').bond[0].order)

        cmd.cycle_valence()
        self.assertEqual(3, cmd.get_model('pkbond').bond[0].order)

    def test_deprotect(self):
        # see test_protect
        pass

    def test_drag(self):
        cmd.drag
        self.skipTest("TODO")

    def test_dss(self):
        ss_list = []
        cmd.fab('A' * 6, ss=1)
        cmd.dss()
        cmd.iterate('2-5/CA', 'ss_list.append(ss)', space=locals())
        self.assertEqual(ss_list, ['H', 'H', 'H', 'H'])

    def test_edit(self):
        cmd.fragment('gly')
        cmd.edit('ID 0', 'ID 1', 'ID 2','ID 3')
        names = cmd.get_names('public_selections')
        self.assertEqual(names, ['pk1', 'pk2', 'pk3', 'pk4', 'pkset', 'pkmol'])

    def test_fix_chemistry(self):
        cmd.fix_chemistry
        self.skipTest("TODO")

    def test_flag(self):
        cmd.flag
        self.skipTest("TODO")

    def test_fuse(self):
        cmd.fragment('ala')
        cmd.fragment('gly')
        cmd.fuse("gly and elem N", "ala and elem O")
        self.assertEqual(17, cmd.count_atoms('ala'))

    def test_get_editor_scheme(self):
        cmd.get_editor_scheme
        self.skipTest("TODO")

    def test_h_add(self):
        cmd.fragment('gly')
        cmd.h_add()
        self.assertEqual(5, cmd.count_atoms('hydro'))

    def test_h_fill(self):
        cmd.fragment('gly')
        cmd.edit('elem N')
        cmd.h_fill()
        self.assertEqual(4, cmd.count_atoms('hydro'))

    def test_h_fix(self):
        cmd.h_fix
        self.skipTest("TODO")

    def test_invert(self):
        cmd.fragment('ala')
        xyzfix = get_coord_list('ID 1-7')
        xyzmov = get_coord_list('ID 0+8+9')
        cmd.edit('ID 1', 'ID 2', 'ID 3')
        cmd.invert()
        self.assertEqual(xyzfix, get_coord_list('ID 1-7'))
        self.assertNotEqual(xyzmov, get_coord_list('ID 0+8+9'))

    def test_map_double(self):
        cmd.map_double
        self.skipTest("TODO")

    def test_map_halve(self):
        cmd.map_halve
        self.skipTest("TODO")

    def test_map_set(self):
        cmd.map_set
        self.skipTest("TODO")

    def test_map_set_border(self):
        cmd.map_set_border
        self.skipTest("TODO")

    def test_map_trim(self):
        cmd.map_trim
        self.skipTest("TODO")

    def test_matrix_copy(self):
        cmd.fragment('ala')
        cmd.fragment('gly')
        cmd.rotate('x', 90, 'none', object='ala')
        cmd.matrix_copy('ala', 'gly')
        self.assertArrayEqual(cmd.get_object_matrix('gly'),
                (1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0,-1.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 1.0), 1e-4)
        cmd.matrix_reset('gly', mode=1)
        self.assertArrayEqual(cmd.get_object_matrix('gly'),
                (1.0, 0.0, 0.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.0, 0.0, 0.0, 1.0), 1e-4)

    def test_matrix_reset(self):
        # see test_matrix_copy
        pass

    def test_protect(self):
        cmd.pseudoatom('m1', pos=[0.,0.,0.])
        cmd.pseudoatom('m1', pos=[1.,0.,0.])

        cmd.protect('m1`1')
        cmd.translate([0.,1.,0.])
        self.assertEqual([0.,0.,0.], cmd.get_atom_coords('m1`1'))
        self.assertEqual([1.,1.,0.], cmd.get_atom_coords('m1`2'))

        cmd.deprotect()
        cmd.translate([0.,0.,1.])
        self.assertEqual([0.,0.,1.], cmd.get_atom_coords('m1`1'))
        self.assertEqual([1.,1.,1.], cmd.get_atom_coords('m1`2'))

    def test_push_undo(self):
        cmd.push_undo
        self.skipTest("TODO")

    def test_redo(self):
        cmd.redo
        self.skipTest("TODO")

    def test_reference(self):
        # undocumented
        cmd.reference
        self.skipTest("TODO")

    def test_remove(self):
        cmd.fragment('ala')
        cmd.remove('elem C')
        self.assertEqual(7, cmd.count_atoms())

    @testing.foreach((0, 7), (1, 3))
    def test_remove_picked(self, hydro, count):
        cmd.fragment('ala')
        cmd.edit('ID 1', 'ID 2', 'ID 3')
        cmd.remove_picked(hydro)
        self.assertEqual(count, cmd.count_atoms())

    def test_rename(self):
        count_names = lambda: len(set([a.name for a in cmd.get_model().atom]))
        cmd.fragment('ala')
        v = cmd.alter('elem C', 'name="C"')
        self.assertEqual(v, 3)
        v1 = count_names()
        cmd.rename('ala')
        v2 = count_names()
        self.assertEqual(v2 - v1, 2)
        self.assertEqual(v2, cmd.count_atoms())

    def test_replace(self):
        # NOTES:
        # - doc says "Immature functionality"
        # - will not preserve ID
        # - will not re-add hydrogens with h_fill=1
        cmd.fragment('ala')
        cmd.edit('elem O')
        cmd.replace('S', 0, 0, 0)
        self.assertEqual(0, cmd.count_atoms('elem O'))
        self.assertEqual(1, cmd.count_atoms('elem S'))

    def test_rotate(self):
        from chempy import cpv
        from math import pi

        get_coord_list = lambda s: cmd.get_model(s).get_coord_list()

        cmd.fragment('ala')
        cmd.select('s1', 'hydro')

        c1_hydro = get_coord_list('s1')
        c1_other = get_coord_list('not s1')
        c1_hydro_rot = cpv.transform_array(
                cpv.rotation_matrix(pi * 0.25, [0,0,1]), c1_hydro)

        cmd.rotate('z', 45, 's1', camera=0, origin=(0,0,0))

        c2_hydro = get_coord_list('s1')
        c2_other = get_coord_list('not s1')

        self.assertArrayEqual(c2_other, c1_other)
        self.assertArrayEqual(c2_hydro, c1_hydro_rot, 0.001)

    def test_sculpt_activate(self):
        cmd.sculpt_activate
        self.skipTest("TODO")

    def test_sculpt_deactivate(self):
        cmd.sculpt_deactivate
        self.skipTest("TODO")

    def test_sculpt_iterate(self):
        cmd.sculpt_iterate
        self.skipTest("TODO")

    def test_sculpt_purge(self):
        cmd.sculpt_purge
        self.skipTest("TODO")

    def test_set_dihedral(self):
        cmd.fragment('ala')
        angle = 45.0
        atoms = ('ID 7', 'ID 2', 'ID 1', 'ID 9')
        cmd.set_dihedral(*atoms, angle=angle)
        v = cmd.get_dihedral(*atoms)
        self.assertAlmostEqual(v, angle, 4)

    def test_set_geometry(self):
        cmd.set_geometry
        self.skipTest("TODO")

    def test_set_name(self):
        cmd.pseudoatom('m1')
        cmd.set_name('m1', 'm2')
        self.assertEqual(['m2'], cmd.get_names())

    def test_set_object_color(self):
        self.skipTest("TODO")

        cmd.fragment('gly')
        cmd.set_object_color('gly', 'blue')
        self.assertEqual('blue', cmd.get('color', 'gly'))

    def test_set_object_ttt(self):
        M = [1.0, 0.0, 0.0, 0.0,
             0.0, 0.0,-1.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 1.0]
        cmd.pseudoatom('m1')
        cmd.set_object_ttt('m1', M)
        self.assertArrayEqual(M, cmd.get_object_matrix('m1'), 1e-4)

    def test_set_symmetry(self):
        sym = [68.7, 126.8, 184.0, 90.0, 90.0, 90.0, 'P 21 21 21']
        cmd.pseudoatom('m1')
        cmd.set_symmetry('m1', *sym)
        v = cmd.get_symmetry('m1')
        self.assertEqual(v[-1], sym[-1])
        self.assertArrayEqual(v[:-1], sym[:-1], 1e-4)

        cmd.pseudoatom('m2')
        cmd.symmetry_copy('m1', 'm2')
        v = cmd.get_symmetry('m2')
        self.assertEqual(v[-1], sym[-1])
        self.assertArrayEqual(v[:-1], sym[:-1], 1e-4)

    def test_set_title(self):
        text = 'foo'
        cmd.pseudoatom('m1')
        cmd.set_title('m1', 1, text)
        self.assertEqual(cmd.get_title('m1', 1), text)

    def test_smooth(self):
        cmd.smooth
        self.skipTest("TODO")

    def test_sort(self):
        cmd.pseudoatom('m1', name='PS2')
        cmd.pseudoatom('m1', name='PS1')
        v = [a.name for a in cmd.get_model().atom]
        self.assertEqual(['PS2', 'PS1'], v)
        cmd.sort()
        v = [a.name for a in cmd.get_model().atom]
        self.assertEqual(['PS1', 'PS2'], v)

    def test_split_states(self):
        cmd.fragment('ala', 'm1')
        cmd.create('m1', 'm1', 1, 2)
        cmd.create('m1', 'm1', 1, 3)
        cmd.split_states('m1', 1, 2)
        self.assertItemsEqual(['m1', 'm1_0001', 'm1_0002'], cmd.get_names())

    def test_symmetry_copy(self):
        # see test_set_symmetry
        pass

    def test_torsion(self):
        cmd.fragment('ala')
        delta = 10
        atoms = ('ID 7', 'ID 2', 'ID 1', 'ID 9')
        d1 = cmd.get_dihedral(*atoms)
        cmd.edit(*atoms[1:3])
        cmd.torsion(delta)
        d2 = cmd.get_dihedral(*atoms)
        self.assertAlmostEqual(d1 + delta, d2, 4)

    def test_transform_object(self):
        cmd.transform_object
        self.skipTest("TODO")

    def test_transform_selection(self):
        cmd.transform_selection
        self.skipTest("TODO")

    def test_translate(self):
        # see test_protect
        pass

    def test_translate_atom(self):
        cmd.translate_atom
        self.skipTest("TODO")

    def test_unbond(self):
        # see test_bond
        pass

    def test_undo(self):
        cmd.undo
        self.skipTest("TODO")

    def test_unpick(self):
        cmd.pseudoatom('m1')
        cmd.edit('m1')
        cmd.unpick()
        self.assertTrue('pk1' not in cmd.get_names('selections'))

    def test_update(self):
        cmd.update
        self.skipTest("TODO")

    def test_valence(self):
        cmd.fragment('gly')
        cmd.valence(2, 'ID 0', 'ID 1')
        self.assertEqual(2, cmd.get_model('ID 0+1').bond[0].order)

    def test_vdw_fit(self):
        cmd.vdw_fit
        self.skipTest("TODO")
