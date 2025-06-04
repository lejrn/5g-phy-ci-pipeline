*** Settings ***
Documentation    5G PHY OFDM Simulation Test Suite
...              Tests the radio simulation pipeline end-to-end
Library          Process
Library          OperatingSystem
Library          String
Library          DateTime

*** Variables ***
${SIMULATION_CMD}    python
@{BASE_ARGS}         -m    radio_sim.main
${TEST_BITS}         5000
${MIN_SNR}           10
${MAX_SNR}           20
${SNR_STEP}          2

*** Test Cases ***
QPSK Simulation Should Complete Successfully
    [Documentation]    Run QPSK simulation and verify it completes without errors
    [Tags]    simulation    qpsk    smoke
    
    ${result}=    Run Process    ${SIMULATION_CMD}
    ...    @{BASE_ARGS}
    ...    --modulation    QPSK
    ...    --bits    ${TEST_BITS}
    ...    --snr-start    ${MIN_SNR}
    ...    --snr-stop    ${MAX_SNR}
    ...    --snr-step    ${SNR_STEP}
    ...    timeout=60s
    
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    Simulation completed successfully
    Should Contain    ${result.stdout}    QPSK
    Log    ${result.stdout}

16-QAM Simulation Should Complete Successfully
    [Documentation]    Run 16-QAM simulation and verify it completes without errors
    [Tags]    simulation    16qam    smoke
    
    ${result}=    Run Process    ${SIMULATION_CMD}
    ...    @{BASE_ARGS}
    ...    --modulation    16QAM
    ...    --bits    ${TEST_BITS}
    ...    --snr-start    15
    ...    --snr-stop    25
    ...    --snr-step    ${SNR_STEP}
    ...    timeout=60s
    
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    Simulation completed successfully
    Should Contain    ${result.stdout}    16QAM
    Log    ${result.stdout}

BER Performance Should Meet Requirements
    [Documentation]    Verify that BER meets performance thresholds at high SNR
    [Tags]    performance    ber    critical
    
    # Run simulation with more bits for accurate BER measurement
    ${result}=    Run Process    ${SIMULATION_CMD}
    ...    @{BASE_ARGS}
    ...    --modulation    QPSK
    ...    --bits    20000
    ...    --snr-start    15
    ...    --snr-stop    20
    ...    --snr-step    1
    ...    timeout=120s
    
    Should Be Equal As Integers    ${result.rc}    0
    
    # Check that no warnings about high BER appear
    Should Not Contain    ${result.stdout}    WARNING: High BER
    
    # Check that simulation reports completion
    Should Contain    ${result.stdout}    Simulation completed successfully
    Log    BER Performance Test Results:
    Log    ${result.stdout}

Simulation Should Handle Different Bit Counts
    [Documentation]    Test simulation with different numbers of bits
    [Tags]    robustness    parameterized
    
    FOR    ${bits}    IN    1000    5000    10000
        ${result}=    Run Process    ${SIMULATION_CMD}
        ...    @{BASE_ARGS}
        ...    --bits    ${bits}
        ...    --snr-start    15
        ...    --snr-stop    20
        ...    --snr-step    5
        ...    timeout=60s
        
        Should Be Equal As Integers    ${result.rc}    0
        Should Contain    ${result.stdout}    Bits per simulation: ${bits}
        Log    Tested with ${bits} bits successfully
    END

Help Option Should Work
    [Documentation]    Verify that help option displays usage information
    [Tags]    cli    help    smoke
    
    ${result}=    Run Process    ${SIMULATION_CMD}
    ...    @{BASE_ARGS}
    ...    --help
    ...    timeout=30s
    
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    5G PHY OFDM Simulation Pipeline
    Should Contain    ${result.stdout}    --modulation
    Should Contain    ${result.stdout}    --bits
    Should Contain    ${result.stdout}    --snr-start

Invalid Parameters Should Fail Gracefully
    [Documentation]    Test that invalid parameters are handled properly
    [Tags]    error-handling    negative
    
    # Test invalid modulation
    ${result}=    Run Process    ${SIMULATION_CMD}
    ...    @{BASE_ARGS}
    ...    --modulation    INVALID
    ...    timeout=30s
    
    Should Not Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stderr}    invalid choice

*** Keywords ***
Get Lines Containing String
    [Arguments]    ${text}    ${string}
    [Documentation]    Extract lines from text that contain a specific string
    
    @{lines}=    Split To Lines    ${text}
    @{matching_lines}=    Create List
    
    FOR    ${line}    IN    @{lines}
        ${contains}=    Run Keyword And Return Status    Should Contain    ${line}    ${string}
        IF    ${contains}
            Append To List    ${matching_lines}    ${line}
        END
    END
    
    ${result}=    Catenate    SEPARATOR=\n    @{matching_lines}
    RETURN    ${result}
