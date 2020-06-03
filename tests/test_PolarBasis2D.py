import numpy as np
from unittest import TestCase

from aspire.basis.polar_2d import PolarBasis2D
from aspire.utils.matlab_compat import m_reshape


class PolarBasis2DTestCase(TestCase):
    def setUp(self):
        self.basis = PolarBasis2D((8, 8), 4, 32)

    def tearDown(self):
        pass

    def testPolarBasis2DEvaluate_t(self):
        x = np.array([
            [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
             -1.08106869e-17,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
            [ 0.00000000e+00,  0.00000000e+00, -6.40456062e-03, -3.32961020e-03,
             -1.36887927e-02, -5.42770488e-03,  7.63680861e-03,  0.00000000e+00],
            [ 0.00000000e+00,  3.16377602e-03, -9.31273350e-03,  9.46128404e-03,
              1.93239220e-02,  3.79891953e-02,  1.06841173e-02, -2.36467925e-03],
            [ 0.00000000e+00,  1.72736955e-03, -1.00710814e-02,  4.93520304e-02,
              3.77702656e-02,  6.57365438e-02,  3.94739462e-03, -4.41228496e-03],
            [ 4.01551066e-18, -3.08071647e-03, -1.61670565e-02,  8.66886286e-02,
              5.09898409e-02,  7.19313349e-02,  1.68313715e-02,  5.19180892e-03],
            [ 0.00000000e+00,  2.87262215e-03, -3.37732956e-02,  4.51706505e-02,
              5.72215879e-02,  4.63553081e-02,  1.86552175e-03,  1.12608805e-02],
            [ 0.00000000e+00,  2.77905016e-03, -2.77499404e-02, -4.02645374e-02,
             -1.54969139e-02, -1.66229153e-02, -2.07389259e-02,  6.64060546e-03],
            [ 0.00000000e+00,  0.00000000e+00,  5.20080934e-03, -1.06788196e-02,
             -1.14761672e-02, -1.27443126e-02, -1.15563484e-02,  0.00000000e+00]
        ])

        pf = self.basis.evaluate_t(x)
        result = np.array(
            [ 0.38243133+6.66608316e-18j,  0.3249317 -1.47839074e-01j,
              0.14819172+3.78171168e-03j, -0.22808599+5.29338933e-02j,
              0.38243133+6.66608316e-18j,  0.34595014-1.06355385e-01j,
              0.15519289-4.75602164e-02j, -0.22401193+4.33128746e-03j,
              0.38243133+6.66608316e-18j,  0.36957165-5.69575709e-02j,
              0.17389327-5.53498385e-02j, -0.11601473-1.35405676e-02j,
              0.38243133+6.66608316e-18j,  0.39045046-2.17911945e-03j,
              0.18146449-1.37089189e-02j, -0.02110144+6.65071497e-03j,
              0.38243133+6.66608316e-18j,  0.4063995 +5.21354967e-02j,
              0.15674204+3.85815662e-02j, -0.02886296+3.91489615e-02j,
              0.38243133+6.66608316e-18j,  0.41872477+9.98946906e-02j,
              0.11862477+5.15231952e-02j, -0.05298751+1.95319478e-02j,
              0.38243133+6.66608316e-18j,  0.43013599+1.38307796e-01j,
              0.10075763+1.25689289e-02j, -0.04052728-5.66863498e-02j,
              0.38243133+6.66608316e-18j,  0.44144497+1.68826980e-01j,
              0.11446016-4.53003874e-02j, -0.03546515-1.13544145e-01j,
              0.38243133+6.66608316e-18j,  0.44960099+1.94794929e-01j,
              0.15053714-8.11915305e-02j, -0.04800556-1.15828804e-01j,
              0.38243133+6.66608316e-18j,  0.44872328+2.17957567e-01j,
              0.19116871-7.99536373e-02j, -0.05683092-9.72225058e-02j,
              0.38243133+6.66608316e-18j,  0.43379428+2.36681249e-01j,
              0.21025378-5.48466438e-02j, -0.05318826-8.54948014e-02j,
              0.38243133+6.66608316e-18j,  0.40485577+2.47073481e-01j,
              0.18680217-3.31766116e-02j, -0.06674163-7.94216591e-02j,
              0.38243133+6.66608316e-18j,  0.36865853+2.45913767e-01j,
              0.13660805-3.68947359e-02j, -0.11467046-8.49198927e-02j,
              0.38243133+6.66608316e-18j,  0.33597018+2.32971425e-01j,
              0.1072859 -6.24686168e-02j, -0.12932565-1.06139634e-01j,
              0.38243133+6.66608316e-18j,  0.31616666+2.10791785e-01j,
              0.11876919-7.93812474e-02j, -0.1094488 -1.20159845e-01j,
              0.38243133+6.66608316e-18j,  0.31313975+1.82190396e-01j,
              0.14075481-5.85637416e-02j, -0.15198775-1.02156797e-01j,
              0.38243133-6.66608316e-18j,  0.3249317 +1.47839074e-01j,
              0.14819172-3.78171168e-03j, -0.22808599-5.29338933e-02j,
              0.38243133-6.66608316e-18j,  0.34595014+1.06355385e-01j,
              0.15519289+4.75602164e-02j, -0.22401193-4.33128746e-03j,
              0.38243133-6.66608316e-18j,  0.36957165+5.69575709e-02j,
              0.17389327+5.53498385e-02j, -0.11601473+1.35405676e-02j,
              0.38243133-6.66608316e-18j,  0.39045046+2.17911945e-03j,
              0.18146449+1.37089189e-02j, -0.02110144-6.65071497e-03j,
              0.38243133-6.66608316e-18j,  0.4063995 -5.21354967e-02j,
              0.15674204-3.85815662e-02j, -0.02886296-3.91489615e-02j,
              0.38243133-6.66608316e-18j,  0.41872477-9.98946906e-02j,
              0.11862477-5.15231952e-02j, -0.05298751-1.95319478e-02j,
              0.38243133-6.66608316e-18j,  0.43013599-1.38307796e-01j,
              0.10075763-1.25689289e-02j, -0.04052728+5.66863498e-02j,
              0.38243133-6.66608316e-18j,  0.44144497-1.68826980e-01j,
              0.11446016+4.53003874e-02j, -0.03546515+1.13544145e-01j,
              0.38243133-6.66608316e-18j,  0.44960099-1.94794929e-01j,
              0.15053714+8.11915305e-02j, -0.04800556+1.15828804e-01j,
              0.38243133-6.66608316e-18j,  0.44872328-2.17957567e-01j,
              0.19116871+7.99536373e-02j, -0.05683092+9.72225058e-02j,
              0.38243133-6.66608316e-18j,  0.43379428-2.36681249e-01j,
              0.21025378+5.48466438e-02j, -0.05318826+8.54948014e-02j,
              0.38243133-6.66608316e-18j,  0.40485577-2.47073481e-01j,
              0.18680217+3.31766116e-02j, -0.06674163+7.94216591e-02j,
              0.38243133-6.66608316e-18j,  0.36865853-2.45913767e-01j,
              0.13660805+3.68947359e-02j, -0.11467046+8.49198927e-02j,
              0.38243133-6.66608316e-18j,  0.33597018-2.32971425e-01j,
              0.1072859 +6.24686168e-02j, -0.12932565+1.06139634e-01j,
              0.38243133-6.66608316e-18j,  0.31616666-2.10791785e-01j,
              0.11876919+7.93812474e-02j, -0.1094488 +1.20159845e-01j,
              0.38243133-6.66608316e-18j,  0.31313975-1.82190396e-01j,
              0.14075481+5.85637416e-02j, -0.15198775+1.02156797e-01j]
        )

        self.assertTrue(np.allclose(pf, result))

    def testPolarBasis2DEvaluate(self):
        v = np.array(
            [ 0.38243133-6.66608316e-18j,  0.3249317 +1.47839074e-01j,
              0.14819172-3.78171168e-03j, -0.22808599-5.29338933e-02j,
              0.38243133-6.66608316e-18j,  0.34595014+1.06355385e-01j,
              0.15519289+4.75602164e-02j, -0.22401193-4.33128746e-03j,
              0.38243133-6.66608316e-18j,  0.36957165+5.69575709e-02j,
              0.17389327+5.53498385e-02j, -0.11601473+1.35405676e-02j,
              0.38243133-6.66608316e-18j,  0.39045046+2.17911945e-03j,
              0.18146449+1.37089189e-02j, -0.02110144-6.65071497e-03j,
              0.38243133-6.66608316e-18j,  0.4063995 -5.21354967e-02j,
              0.15674204-3.85815662e-02j, -0.02886296-3.91489615e-02j,
              0.38243133-6.66608316e-18j,  0.41872477-9.98946906e-02j,
              0.11862477-5.15231952e-02j, -0.05298751-1.95319478e-02j,
              0.38243133-6.66608316e-18j,  0.43013599-1.38307796e-01j,
              0.10075763-1.25689289e-02j, -0.04052728+5.66863498e-02j,
              0.38243133-6.66608316e-18j,  0.44144497-1.68826980e-01j,
              0.11446016+4.53003874e-02j, -0.03546515+1.13544145e-01j,
              0.38243133-6.66608316e-18j,  0.44960099-1.94794929e-01j,
              0.15053714+8.11915305e-02j, -0.04800556+1.15828804e-01j,
              0.38243133-6.66608316e-18j,  0.44872328-2.17957567e-01j,
              0.19116871+7.99536373e-02j, -0.05683092+9.72225058e-02j,
              0.38243133-6.66608316e-18j,  0.43379428-2.36681249e-01j,
              0.21025378+5.48466438e-02j, -0.05318826+8.54948014e-02j,
              0.38243133-6.66608316e-18j,  0.40485577-2.47073481e-01j,
              0.18680217+3.31766116e-02j, -0.06674163+7.94216591e-02j,
              0.38243133-6.66608316e-18j,  0.36865853-2.45913767e-01j,
              0.13660805+3.68947359e-02j, -0.11467046+8.49198927e-02j,
              0.38243133-6.66608316e-18j,  0.33597018-2.32971425e-01j,
              0.1072859 +6.24686168e-02j, -0.12932565+1.06139634e-01j,
              0.38243133-6.66608316e-18j,  0.31616666-2.10791785e-01j,
              0.11876919+7.93812474e-02j, -0.1094488 +1.20159845e-01j,
              0.38243133-6.66608316e-18j,  0.31313975-1.82190396e-01j,
              0.14075481+5.85637416e-02j, -0.15198775+1.02156797e-01j,
              0.38243133+6.66608316e-18j,  0.3249317 -1.47839074e-01j,
              0.14819172+3.78171168e-03j, -0.22808599+5.29338933e-02j,
              0.38243133+6.66608316e-18j,  0.34595014-1.06355385e-01j,
              0.15519289-4.75602164e-02j, -0.22401193+4.33128746e-03j,
              0.38243133+6.66608316e-18j,  0.36957165-5.69575709e-02j,
              0.17389327-5.53498385e-02j, -0.11601473-1.35405676e-02j,
              0.38243133+6.66608316e-18j,  0.39045046-2.17911945e-03j,
              0.18146449-1.37089189e-02j, -0.02110144+6.65071497e-03j,
              0.38243133+6.66608316e-18j,  0.4063995 +5.21354967e-02j,
              0.15674204+3.85815662e-02j, -0.02886296+3.91489615e-02j,
              0.38243133+6.66608316e-18j,  0.41872477+9.98946906e-02j,
              0.11862477+5.15231952e-02j, -0.05298751+1.95319478e-02j,
              0.38243133+6.66608316e-18j,  0.43013599+1.38307796e-01j,
              0.10075763+1.25689289e-02j, -0.04052728-5.66863498e-02j,
              0.38243133+6.66608316e-18j,  0.44144497+1.68826980e-01j,
              0.11446016-4.53003874e-02j, -0.03546515-1.13544145e-01j,
              0.38243133+6.66608316e-18j,  0.44960099+1.94794929e-01j,
              0.15053714-8.11915305e-02j, -0.04800556-1.15828804e-01j,
              0.38243133+6.66608316e-18j,  0.44872328+2.17957567e-01j,
              0.19116871-7.99536373e-02j, -0.05683092-9.72225058e-02j,
              0.38243133+6.66608316e-18j,  0.43379428+2.36681249e-01j,
              0.21025378-5.48466438e-02j, -0.05318826-8.54948014e-02j,
              0.38243133+6.66608316e-18j,  0.40485577+2.47073481e-01j,
              0.18680217-3.31766116e-02j, -0.06674163-7.94216591e-02j,
              0.38243133+6.66608316e-18j,  0.36865853+2.45913767e-01j,
              0.13660805-3.68947359e-02j, -0.11467046-8.49198927e-02j,
              0.38243133+6.66608316e-18j,  0.33597018+2.32971425e-01j,
              0.1072859 -6.24686168e-02j, -0.12932565-1.06139634e-01j,
              0.38243133+6.66608316e-18j,  0.31616666+2.10791785e-01j,
              0.11876919-7.93812474e-02j, -0.1094488 -1.20159845e-01j,
              0.38243133+6.66608316e-18j,  0.31313975+1.82190396e-01j,
              0.14075481-5.85637416e-02j, -0.15198775-1.02156797e-01j]
        )

        x = self.basis.evaluate(v)
        result = np.array(
            [[ 9.8593804 -1.71301803e-15j,  7.94242903-2.29300667e-15j,
               7.23336975-2.38349504e-15j,  7.33314303-1.68542720e-15j,
               7.41260132-4.36233426e-15j,  7.59483694-5.35891413e-15j,
               7.94830958-1.21589336e-15j,  9.47324547-1.46703657e-15j],
             [ 7.27801941-4.54693517e-15j,  8.29797686-2.39294616e-15j,
               7.17234599-2.51916150e-15j,  7.31082685-1.28638530e-15j,
               7.04347376-3.12626429e-15j,  6.91956664-5.24845304e-15j,
               8.12234596-6.20927767e-16j,  8.36258646+1.56528419e-15j],
             [ 8.76188511-7.29507183e-15j, 10.69546884-3.29125191e-15j,
               8.37029969-1.56100041e-15j,  9.87512737+3.55731989e-17j,
               9.73946157+2.18714331e-17j,  6.56646752-1.58621718e-15j,
               5.69555713+8.59263220e-16j,  8.77758976+3.50812304e-15j],
             [10.42069436-7.56330235e-15j, 12.3649092 -3.27383286e-15j,
              14.23951952+1.64244016e-16j, 20.41736454+9.54489541e-16j,
              22.32664939+2.20731883e-16j, 18.11535113-1.26928040e-15j,
              7.95059873+7.19579935e-16j,  8.79515046+3.74341388e-15j],
             [11.23152882-5.73469963e-15j, 12.61468396-3.05914884e-15j,
              17.92585027+3.94218502e-16j, 25.82097043+1.64003130e-15j,
              26.4633412 +6.00971336e-18j, 25.11167661-1.05488885e-15j,
              11.90634511+2.69486345e-15j,  9.05131389+4.50141438e-15j],
             [10.7048523 -6.68266622e-15j, 11.73534566-5.14272145e-15j,
              16.53838035-1.67517565e-15j, 25.13242621+5.97549153e-16j,
              23.58037996-5.25666358e-16j, 21.37129485-2.67235158e-15j,
              12.1024389 +5.79222586e-16j, 10.26313743+5.46829708e-15j],
             [ 8.24162377-7.77724318e-15j, 11.90490143-3.38771193e-15j,
              14.82292441+1.46743199e-15j, 19.50174891+2.32986604e-15j,
              17.69291969+3.40473980e-16j, 15.06781768-1.22685993e-15j,
              10.4669263 +2.53487440e-16j, 10.2082326 +6.19705593e-15j],
             [ 5.26532858-4.92458818e-15j,  9.60999648-1.50636013e-15j,
              12.68642275+2.21945377e-15j, 12.42354237+4.22538880e-15j,
              10.87648517+2.33148336e-15j, 10.60647963+1.40329822e-15j,
               9.11026567+7.00211842e-16j,  8.53250276+4.84351417e-15j]]
        )

        self.assertTrue(np.allclose(x, result))

    def testPolarBasis2DAdjoint(self):
        # The evaluate function should be the adjoint operator of evaluate_t.
        # Namely, if A = evaluate, B = evaluate_t, and B=A^t, we will have
        # (y, A*x) = (A^t*y, x) = (B*y, x)
        x = np.random.randn(self.basis.count)

        x = m_reshape(x, (self.basis.nrad, self.basis.ntheta))

        x = (1 / 2 * x[:, :self.basis.ntheta // 2]
             + 1 / 2 * x[:, :self.basis.ntheta // 2].conj())

        x = np.concatenate((x, x.conj()), axis=1)

        x = m_reshape(x, (self.basis.nrad * self.basis.ntheta,))

        x_t = self.basis.evaluate(x)
        y = np.random.randn(np.prod(self.basis.sz))
        y_t = self.basis.evaluate_t(m_reshape(y, self.basis.sz))
        self.assertTrue(np.isclose(np.dot(y, m_reshape(x_t, (np.prod(self.basis.sz),))),
                                   np.dot(y_t, x)))
