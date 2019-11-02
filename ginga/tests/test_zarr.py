import hashlib
import numpy as np
import pytest

zarr = pytest.importorskip('zarr')

from ginga import AstroImage, trcalc
from ginga.misc import log


class TestZarr:
    def setup_class(self):
        self.logger = log.get_logger("TestZarr", null=True)

    def _2ddata(self, shape, data_np=None):
        if data_np is None:
            data_np = np.asarray([min(i, j)
                                  for i in range(shape[0])
                                  for j in range(shape[1])])
        data_np = data_np.reshape(shape)
        data_z = zarr.creation.array(data_np, chunks=(10, 10))
        return data_z

    def _3ddata(self, shape, data_np=None):
        if data_np is None:
            data_np = np.asarray([min(i, j, k)
                                  for i in range(shape[0])
                                  for j in range(shape[1])
                                  for k in range(shape[2])])
        data_np = data_np.reshape(shape)
        data_z = zarr.creation.array(data_np, chunks=(10, 10, 10))
        return data_z

    def test_zarr_slice_trcalc(self):
        """Test that we can get a subslice of a zarr.
        """
        arr_z = self._2ddata((1000, 500))

        x_slice, y_slice = slice(12, 499, 3), slice(10, 951, 11)
        view = (y_slice, x_slice)
        data_np = trcalc.fancy_index(arr_z, view)
        assert isinstance(data_np, np.ndarray)
        assert data_np.shape == (86, 163)
        assert isinstance(data_np[0, 0], np.integer)
        res = 'be219a7516d02d3c3fd399f66af68ddec820496da09c0646e23c7c6437155fee'
        m = hashlib.sha256()
        m.update(np.asarray(data_np).tobytes())
        assert m.hexdigest() == res

    def test_zarr_slice_aimg(self):
        """Test that we can get a subslice of an AstroImage object.
        """
        aimg = AstroImage.AstroImage(logger=self.logger)
        aimg.set_data(self._2ddata((700, 800)))

        x_slice, y_slice = slice(12, 800, 8), slice(0, 700, 10)
        view = (y_slice, x_slice)
        data_np = aimg._slice(view)
        assert isinstance(data_np, np.ndarray)
        assert data_np.shape == (70, 99)
        assert isinstance(data_np[0, 0], np.integer)
        res = '39f4fe77ed29b083ad18e692baa27cecbd48fc835f515070b3d7f8b6fe81a741'
        m = hashlib.sha256()
        m.update(data_np.tobytes())
        assert m.hexdigest() == res

    def test_zarr_aimg_get_data_xy(self):
        """Test that we can get a single value from an AstroImage object.
        """
        aimg = AstroImage.AstroImage(logger=self.logger)
        aimg.set_data(self._2ddata((5, 5), data_np=np.arange(0, 25)))

        val = int(aimg.get_data_xy(3, 3))
        assert isinstance(val, int)
        assert val == 18

    def test_zarr_fancy_scale(self):
        """Test that we can get a fancy superslice of a zarr.
        """
        arr_z = self._3ddata((5, 5, 5))

        p1 = (0, 0, 0)
        p2 = (5, 5, 5)
        new_dims = (51, 51, 51)

        data_np, scales = trcalc.get_scaled_cutout_wdhtdp(arr_z, p1, p2,
                                                          new_dims,
                                                          logger=self.logger)
        assert isinstance(data_np, np.ndarray)
        assert data_np.shape == new_dims
        assert isinstance(data_np[0, 0, 0], np.integer)
        res = 'e60bfb1ae30b2b5c5261bc288d344f6c4ec7715ca17cdd65d9ad50f91911f0a4'
        m = hashlib.sha256()
        m.update(data_np.tobytes())
        assert m.hexdigest() == res
