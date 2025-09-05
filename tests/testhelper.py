import os
import difflib
from glob import glob


def get_test_names(category: str):
    fnames = glob(f"{category}_*.pygraph", root_dir="tests/graphs")
    tnames = [os.path.splitext(fname)[0][(len(category)+1):] for fname in fnames]
    return tnames


def run_export_and_compare(pycnv, testfolder, test_name):
    """Loads the graph, runs an export on it, compares the file to the
    expected, prints the diff and asserts equality.
    """
    fname_graph = os.path.join(testfolder, 'graphs', test_name+'.pygraph')
    fname_result = os.path.join(testfolder, 'results', test_name+'.py')
    fname_expected = os.path.join(testfolder, 'expected', test_name+'.py')

    pycnv.graphLoader(fname_graph)
    pycnv.exporter(pycnv.app, fname_result)

    with open(fname_result, 'r', encoding='utf8') as f1, \
         open(fname_expected, 'r', encoding='utf8') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()

    diff = difflib.unified_diff(f1_lines, f2_lines, 
                                fromfile='result', tofile='expected')
    print(''.join(diff))

    assert len(f1_lines)==len(f2_lines), "Line count difference"
    for i, line1 in enumerate(f1_lines):
        if i!=4: # because that line contains the date
            assert line1==f2_lines[i], \
                   f"Line {i} differs\n--  {line1}\n++  {f2_lines[i]}"
