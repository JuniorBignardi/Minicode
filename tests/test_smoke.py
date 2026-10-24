def test_package_imports():
    import minicode
    import minicode.agent
    import minicode.cli.main
    import minicode.evaluator
    import minicode.llm
    import minicode.safety
    import minicode.spec
    import minicode.tools
    import minicode.tracing

    assert minicode is not None
