# pylint: disable=redefined-builtin, unused-argument
from mdls import hookspec


@hookspec
def mdls_code_actions(config, workspace, document, range, context):
    pass


@hookspec
def mdls_code_lens(config, workspace, document):
    pass


@hookspec
def mdls_commands(config, workspace):
    """The list of command strings supported by the server.

    Returns:
        List[str]: The supported commands.
    """


@hookspec
def mdls_completions(config, workspace, document, position):
    pass


@hookspec
def mdls_definitions(config, workspace, document, position):
    pass


@hookspec
def mdls_dispatchers(config, workspace):
    pass


@hookspec
def mdls_document_did_open(config, workspace, document):
    pass


@hookspec
def mdls_document_did_save(config, workspace, document):
    pass


@hookspec
def mdls_document_highlight(config, workspace, document, position):
    pass


@hookspec
def mdls_document_symbols(config, workspace, document):
    pass

@hookspec
def mdls_workspace_symbols(config, workspace, query):
    pass


@hookspec(firstresult=True)
def mdls_execute_command(config, workspace, command, arguments):
    pass


@hookspec
def mdls_experimental_capabilities(config, workspace):
    pass


@hookspec(firstresult=True)
def mdls_folding_range(config, workspace, document):
    pass


@hookspec(firstresult=True)
def mdls_format_document(config, workspace, document):
    pass


@hookspec(firstresult=True)
def mdls_format_range(config, workspace, document, range):
    pass


@hookspec(firstresult=True)
def mdls_hover(config, workspace, document, position):
    pass


@hookspec
def mdls_initialize(config, workspace):
    pass


@hookspec
def mdls_initialized():
    pass


# @hookspec
# def mdls_lint(config, workspace, document, is_saved):
#     pass


@hookspec
def mdls_references(config, workspace, document, position, exclude_declaration):
    pass


@hookspec(firstresult=True)
def mdls_rename(config, workspace, document, position, new_name):
    pass


@hookspec
def mdls_settings(config):
    pass


@hookspec(firstresult=True)
def mdls_signature_help(config, workspace, document, position):
    pass
