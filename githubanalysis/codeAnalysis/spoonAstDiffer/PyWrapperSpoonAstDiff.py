import os

from githubanalysis.common.ConfigFileParser import GlobalConfig
from githubanalysis.common.Logger import Logger
from githubanalysis.common.collectionUtils import safely_append_to_array_in_dict

from githubanalysis.common.constants import SPOON_AST_DIFF_EXCEPTION_DURING_DIFF

global_config = GlobalConfig()
os.environ['JAVA_HOME'] = global_config.java_home
os.environ['CLASSPATH'] = global_config.gumtree_spoon_jar_path

from jnius import autoclass  # install pyjnius! NOT jnius
from jnius import JavaException

DISTILLER_CHANGED_ENTITY_KEY = "changedEntity"
DISTILLER_CHANGE_TYPE_KEY = "changeType"

log = Logger()

class PyWrapperSpoonAstDiff:
    def __init__(self):
        self.J_AstComparator = autoclass("gumtree.spoon.AstComparator")
        self.J_Diff = autoclass("gumtree.spoon.diff.Diff")
        self.J_Operation = autoclass("gumtree.spoon.diff.operations.Operation")
        self.J_Class = autoclass("java.lang.Class")
        self.J_File = autoclass("java.io.File")

    def diff_java(self, old_java, new_java):
        distilled_changes = {}

        # old_file = self.J_File(old_file_path)
        # new_file = self.J_File(new_file_path)
        ast_comparator = self.J_AstComparator()
        try:
            diff = ast_comparator.compare(old_java, new_java)

            operations = diff.getRootOperations().toArray()
            for operation in operations:
                entity = operation.getAction().getNode().getMetadata("type")
                change_type = operation.getAction().getName()
                root = operation.getMethodIdentifier()
                item = {DISTILLER_CHANGED_ENTITY_KEY: entity, DISTILLER_CHANGE_TYPE_KEY: change_type}
                safely_append_to_array_in_dict(distilled_changes, root, item)
            return distilled_changes
        except JavaException as exception:
            log.s(str(exception))
            return {SPOON_AST_DIFF_EXCEPTION_DURING_DIFF: ""}
