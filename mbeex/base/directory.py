import os
import os.path
from pathlib import Path


def stem_name(file_name):
    """Return the files stem (string w/o directory and extension part)"""

    return Path(Path(file_name).name).stem


def count_files(root):
    """Count all files in a directory tree."""

    ret = 0
    for dirpath, dirs, files in os.walk(root):
        for file in files:
            ret += 1
    return ret


def filter_directory(root, filter, *args, print_progress=False):
    """
    Return a subset of file names below root, using a
    filter function (or functor - overload `__call__`)
    `filter(file_name, *args) -> bool`
    
    For `filter == None`, every file will be returned.
    """

    all = count_files(root)
    cnt = 0
    percent = 0
    old_percent = 0
    ret = []
    for dirpath, dirs, files in os.walk(root):
        for file in files:
            ifile = os.path.join(dirpath, file)
            if print_progress == True:
                cnt += 1
                percent = (100 * cnt) // all
                print(
                    f"Filtering directory tree: {percent}% ({cnt}/{all} files)",
                    end="\r",
                )
                percent = old_percent
            if filter == None or filter(ifile, *args):
                ret.append(ifile)
    if print_progress == True:
        print("")
    return ret


def replicate_dir(iroot, relpath, oroot):
    """
    Replicate some part of `iroots` directory structure (described by relative path `relpath`)
    in `oroot` on the fly.
    Returns path string of the newly created or existing directory under `oroot` 
    """

    structure = os.path.join(oroot, os.path.relpath(relpath, iroot))
    if not os.path.isdir(structure):
        os.makedirs(structure)
    return structure


class DirectoryWalker:
    """
    Generic directory walker (reading or/and writing)
    
    Parameters:
        :src: source directory
        :dst: destination directory
    """

    def __init__(self, src, dst):
        self.setDirectories(src, dst)

    def setDirectories(self, src, dst):
        """
        Set source and destination directory for walking

        Parameters:
            :src: source directory
            :dst: destination directory
        """

        self.src_dir = src
        self.dst_dir = dst

    def createFilteredData(self, filter, *args):
        """
        Duplicate `self.src_dir` into identical
        tree structure in `self.dst_dir` with the contained files transformed
        using a filter function (or functor [overload `__call__`])
        `filter(ifile, ofile, *args)`
        """

        all = count_files(self.src_dir)
        cnt = 0
        percent = 0
        old_percent = 0
        print(f"Progress: {percent}% ({cnt}/{all} files)", end="\r")
        for dirpath, dirs, files in os.walk(self.src_dir):
            structure = replicate_dir(self.src_dir, dirpath, self.dst_dir)
            for file in files:
                ifile = os.path.join(dirpath, file)
                ofile = os.path.join(structure, file)
                filter(ifile, ofile, *args)
                cnt += 1
                percent = (100 * cnt) // all
                print(f"Progress: {percent}% ({cnt}/{all} files)", end="\r")
                percent = old_percent

    def run(self, f, multiple=False):
        """
        Traverse `self.src_dir` directory tree, recreate mirror tree in self.dst_dir on the fly and apply
        functor `f` to every allowed source file. `f` can map files 1:1 and n:1
        """

        for curpath, subdirs, files in os.walk(self.src_dir):
            structure = replicate_dir(self.src_dir, curpath, self.dst_dir)
            if not multiple:
                for file in files:
                    ifile = os.path.normpath(os.path.join(curpath, file))
                    f(ifile, structure)
            else:
                if files:
                    ifiles = f.selectInputFiles(files)
                    ifiles = [
                        os.path.normpath(os.path.join(curpath, ifile))
                        for ifile in ifiles
                    ]
                    f(ifiles, structure)


class FileFilter:
    """
    Filters files by suffix and extension lists.
    
    Suffix lists contain allowed endings
    of a filenames stem (defined as name w/o directory path and extension).
    
    Extension lists contain allowed file extensions
    
    Example:
        suffix list   : ['_PARTS', '_PARTS_BB', '_ST']
        extension list: ['xml','png']
    """

    def __init__(self):
        self.valid_extensions = None
        self.valid_suffixes = None

    def setValidExtensions(self, valid_extensions):
        """
        Select, which file types are processed.
        All extensions in `valid_extensions` are allowed.
        """

        self.valid_extensions = valid_extensions

    def setValidSuffixes(self, valid_suffixes):
        """
        Select, which file types are processed.
        All suffixes of the filenames stem in `valid_suffixes`
        are allowed.
        """

        self.valid_suffixes = valid_suffixes

    def validExtension(self, file):
        """
        Check, if the file has a valid extension.
        """

        if not self.valid_extensions or [
            ext for ext in self.valid_extensions if file.lower().endswith("." + ext)
        ]:
            return True
        return False

    def validParticularSuffix(self, file, suffix):
        """
        Check, if the `file` has a specific suffix.
        """

        if not self.valid_suffixes or os.path.splitext(file)[0].endswith(suffix):
            return True
        return False

    def replaceSuffix(self, file, new_suffix):
        """
        If `file` ends with a valid suffix the function returns
        a new file name with this suffix replaced by new_suffix.
        Otherwise an empty string is returned
        """

        if not self.valid_suffixes:
            return ""
        for s in self.valid_suffixes:
            n = stem_name(file)
            if n.endswith(s):
                n = n[: -len(s)] + new_suffix
                pf = Path(file)
                dir = pf.parents[0]
                ext = pf.suffix
                return str(dir / Path(n)) + ext
        return ""

    def validSuffix(self, file):
        """
        Check, if the file has a valid suffix.
        """

        if not self.valid_suffixes or [
            s for s in self.valid_suffixes if os.path.splitext(file)[0].endswith(s)
        ]:
            return True
        return False

    def validFileName(self, file):
        """
        Check, if the file has valid extension and suffix.
        """

        return self.validSuffix(file) and self.validExtension(file)
