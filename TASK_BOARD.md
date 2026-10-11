# Team Task Board

A task is done only when acceptance checks pass and the change is
reviewed.

  ---------------------------------------------------------------------------------------------
  ID          Task                   Owner         Status      Depends on    Evidence
  ----------- ---------------------- ------------- ----------- ------------- ------------------
  T01         Create repo and invite Integration   Not started None          All three have
              collaborators          lead                                    access

  T02         Approve master plan    All           Not started T01           Acknowledgements

  T03         Freeze interfaces and  All           Not started T02           Approved
              conventions                                                    `INTERFACES.md`

  T04         Test clean Colab       Integration   Not started T01           Actual smoke-test
              environment            lead                                    output

  T05         Problem                Member 1      Not started T03           Tests pass
              validation/objective                                           
              evaluator                                                      

  T06         QUBO and               Member 1      Not started T05           Test evidence
              all-16-bitstring                                               
              checks                                                         

  T07         Exact feasible         Member 1      Not started T05           Six feasible
              classical baseline                                             portfolios
                                                                             evaluated

  T08         QAOA `p=1` test QUBO   Member 2      Not started T03           Executed decoding
                                                                             tests

  T09         Validate processor     Member 3      Not started T03           Tests pass
              topology                                                       

  T10         Transpilation metric   Member 3      Not started T09           Test circuit
              collection                                                     outputs

  T11         Integrate QUBO and     Integration   Not started T06,T07,T08   Integration tests
              QAOA                   lead +                                  
                                     Members 1/2                             

  T12         Benchmark same circuit Member 3      Not started T10,T11       Saved benchmark
              on A/B                                                         outputs

  T13         Final notebook,        All           Not started T12           Clean run and
              tables, report                                                 review
  ---------------------------------------------------------------------------------------------

Status values: Not started, In progress, Blocked, In review, Done. Do
not mark a task done because AI generated code or because a test was not
executed.
