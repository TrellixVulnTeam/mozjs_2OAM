# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, unicode_literals
import os
import tempfile
import mozunit
import shutil
import tarfile
import sys

# need this so raptor imports work both from /raptor and via mach
here = os.path.abspath(os.path.dirname(__file__))

raptor_dir = os.path.join(os.path.dirname(here), "raptor")
sys.path.insert(0, raptor_dir)

from gecko_profile import GeckoProfile


def test_browsertime_profiling():
    result_dir = tempfile.mkdtemp()
    # untar geckoProfile.tar
    with tarfile.open(os.path.join(here, "geckoProfile.tar")) as f:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f, path=result_dir)

    # Makes sure we can run the profile process against a browsertime-generated
    # profile (geckoProfile-1.json in this test dir)
    upload_dir = tempfile.mkdtemp()
    symbols_path = tempfile.mkdtemp()
    raptor_config = {
        "symbols_path": symbols_path,
        "browsertime": True,
        "browsertime_result_dir": result_dir,
    }
    test_config = {"name": "tp6"}
    try:
        profile = GeckoProfile(upload_dir, raptor_config, test_config)
        profile.symbolicate()
        profile.clean()
        arcname = os.environ["RAPTOR_LATEST_GECKO_PROFILE_ARCHIVE"]
        assert os.stat(arcname).st_size > 1000000, "We got a 1mb+ zip"
    finally:
        shutil.rmtree(upload_dir)
        shutil.rmtree(symbols_path)
        shutil.rmtree(result_dir)


if __name__ == "__main__":
    mozunit.main()
