import Foundation
import PersonalMythForgeMobileCore

do {
    try testDecodesObjectCaptureFixture()
    try testDecodesMythSessionFixture()
    try testDecodesMythSessionWithoutGeneratedAssetVariants()
    try testDecodesMythSessionWithoutGenerationProvenance()
    try testDecodesMythSessionWithoutNPCAgentTraceFields()
    try testDecodesNPCAgentTickPayload()
    try testDecodesMythSessionHistoryPayload()
    try testDecodesNPCAutonomyRunPayload()
    try testNPCRitualSceneBuildsThreeActorsFromSession()
    try testNPCRitualSceneUsesLatestTickActions()
    try testNPCRitualSceneBackfillsSparseLatestTick()
    try testNPCRitualSceneRedactsUnsafeText()
    try testDemoRunSnapshotKeepsMatchingTicksSortedAndBounded()
    try testDemoRunSnapshotEncodesSnakeCaseJSONWithoutRawMediaOrSecrets()
    try testDemoRunSnapshotFileStoreSavesLoadsOverwritesAndClears()
    try testDecodesProviderReadinessPayload()
    try testNPCAgentModeWaitsForSession()
    try testNPCAgentModeShowsLocalDemoRuntime()
    try testNPCAgentModeShowsOpenAIReadyRuntime()
    try testNPCAgentModeShowsMissingOpenAIKey()
    try testNPCAgentModeUsesLatestTickRuntime()
    try testNPCAgentModeRedactsUnsafeText()
    try testNPCAgentTickSummaryWaitsBeforeSession()
    try testNPCAgentTickSummaryShowsInitialSessionTraces()
    try testNPCAgentTickSummaryShowsLatestTickResolution()
    try testNPCAgentTickSummaryShowsAutonomyRunning()
    try testNPCAgentTickSummaryRedactsUnsafeText()
    try testNPCAgentActionGateDisablesWithoutSession()
    try testNPCAgentActionGateEnablesLocalDemoActions()
    try testNPCAgentActionGateDisablesMissingOpenAISetup()
    try testNPCAgentActionGateDisablesWhileAutonomyRuns()
    try testNPCAgentActionGateRedactsUnsafeDetail()
    try testDecodesPrintQuotePayload()
    try testPrintFulfillmentReceiptWaitsForQuote()
    try testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff()
    try testPrintFulfillmentReceiptShowsApprovedProviderHandoff()
    try testPrintFulfillmentReceiptHandlesNoApprovalRequiredQuote()
    try testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText()
    try testShowcaseEvidenceWaitsForSession()
    try testShowcaseEvidenceMarksReadyLocalDemo()
    try testShowcaseEvidenceBlocksFailedSceneProof()
    try testShowcaseEvidenceRedactsUnsafeDetails()
    try testFinalShowcaseSummaryWaitsBeforeSession()
    try testFinalShowcaseSummaryReadyForLocalDemo()
    try testFinalShowcaseSummaryMarksPrintQuoteReady()
    try testFinalShowcaseSummaryMarksProviderErrorNeedsAttention()
    try testFinalShowcaseSummaryRedactsUnsafeSourceText()
    try testFinalShowcaseSummaryIncludesBlockedFinalLaunchDigest()
    try testFinalShowcaseFinalLaunchStageUsesReceiptFirstBlocker()
    try testFinalShowcaseSummaryIncludesReadyFinalLaunchDigest()
    try testFinalShowcaseSummaryIncludesReadyProviderHandoffDigest()
    try testFinalShowcaseSummaryBlocksProviderHandoffDigest()
    try testFinalShowcaseSummaryBlocksProviderHandoffOnConfiguredEvidenceBundle()
    try testFinalShowcaseSummaryRedactsUnsafeConfiguredBundleProviderHandoff()
    try testFinalShowcaseSummaryRedactsUnsafeProviderHandoffDigest()
    try testFinalShowcaseSummaryIncludesReadyLocalSmokeDigest()
    try testFinalShowcaseSummaryBlocksFailedLocalSmokeDigest()
    try testFinalShowcaseSummaryIncludesReadyIOSDeployDigest()
    try testFinalShowcaseSummaryBlocksIOSDeployDigest()
    try testFinalShowcaseSummaryRedactsUnsafeIOSDeployDigest()
    try testFinalShowcaseSummaryIncludesReadyThreeDEvaluationDigest()
    try testFinalShowcaseSummaryWaitsForMissingThreeDEvaluationDigest()
    try testFinalShowcaseSummaryWaitsForMissingNPCEvaluationDigest()
    try testFinalShowcaseSummaryRedactsUnsafeThreeDEvaluationDigest()
    try testFinalShowcaseSummaryRedactsUnsafeFinalLaunchDigest()
    try testContextCapsuleReviewWaitsForMissingSummary()
    try testContextCapsuleReviewWaitsForApproval()
    try testContextCapsuleReviewMarksApprovedSummaryReady()
    try testContextCapsuleReviewRedactsUnsafeText()
    try testForgeReadinessWaitsForCapture()
    try testForgeReadinessWaitsForContextApproval()
    try testForgeReadinessMarksLocalDemoReady()
    try testForgeReadinessMarksProviderErrorNeedsAttention()
    try testForgeReadinessMarksMissingConfiguredProviders()
    try testForgeReadinessRedactsUnsafeText()
    try testForgeActionGateDisablesWithoutCapture()
    try testForgeActionGateDisablesUntilContextApproved()
    try testForgeActionGateDisablesWhenReadinessNeedsAttention()
    try testForgeActionGateEnablesLocalDemoForge()
    try testForgeActionGateRedactsUnsafeDetail()
    try testDevicePreflightBlocksLoopbackBackendURL()
    try testDevicePreflightWaitsForUncheckedBackendHealth()
    try testDevicePreflightMarksBackendHealthChecking()
    try testDevicePreflightMarksReachableBackendHealthReady()
    try testDevicePreflightBlocksUnreachableBackendHealthAndRedacts()
    try testDevicePreflightBlocksNonOKBackendHealth()
    try testDevicePreflightKeepsLoopbackBlockedWithReachableHealth()
    try testDevicePreflightWaitsForProviderReadiness()
    try testDevicePreflightBlocksAndRedactsProviderError()
    try testDevicePreflightWaitsForFinalLaunchReport()
    try testDevicePreflightUsesFinalLaunchFirstBlockerDetail()
    try testDevicePreflightMapsFinalLaunchPartialToWaiting()
    try testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting()
    try testDevicePreflightMarksReadyFinalResourcesPreflight()
    try testDevicePreflightBlocksAndRedactsFinalResourcesPreflight()
    try testDevicePreflightWaitsForMissingFinalResourceRequirements()
    try testDevicePreflightBlocksOnFinalResourceRequirementsFirstBlocker()
    try testDevicePreflightMarksReadyFinalResourceRequirements()
    try testDevicePreflightRedactsUnsafeFinalResourceRequirementsFirstBlockerDetail()
    try testDevicePreflightWaitsForMissingFinalResourceFillGuide()
    try testDevicePreflightBlocksOnRequiredFinalResourceFillGuideInputs()
    try testDevicePreflightMarksReadyFinalResourceFillGuide()
    try testDevicePreflightRedactsUnsafeFinalResourceFillGuideDetail()
    try testDevicePreflightRedactsUnsafeFinalResourceFillGuideFirstBlockerDetail()
    try testDevicePreflightWaitsForMissingFinalResourceApplyPreview()
    try testDevicePreflightBlocksOnFinalResourceApplyPreviewFirstBlocker()
    try testDevicePreflightMarksReadyFinalResourceApplyPreview()
    try testDevicePreflightRedactsUnsafeFinalResourceApplyPreviewFirstBlockerDetail()
    try testDevicePreflightWaitsForMissingIOSDeployRunbook()
    try testDevicePreflightBlocksOnIOSDeployRunbookCommandStep()
    try testDevicePreflightMarksReadyIOSDeployRunbook()
    try testDevicePreflightRedactsUnsafeIOSDeployRunbookDetail()
    try testDevicePreflightWaitsForMissingIOSDeviceEvidenceBundle()
    try testDevicePreflightBlocksOnIOSDeviceEvidenceSlot()
    try testDevicePreflightMarksReadyIOSDeviceEvidenceBundle()
    try testDevicePreflightRedactsUnsafeIOSDeviceEvidenceBundleDetail()
    try testDevicePreflightWaitsForMissingIOSLaunchRehearsalReadiness()
    try testDevicePreflightBlocksOnIOSLaunchRehearsalReadiness()
    try testDevicePreflightMarksReadyIOSLaunchRehearsalReadiness()
    try testDevicePreflightShowsStaleIOSLaunchRehearsalFreshness()
    try testDevicePreflightRedactsUnsafeIOSLaunchRehearsalReadiness()
    try testDevicePreflightWaitsForMissingIOSDeviceLaunchCertificate()
    try testDevicePreflightBlocksOnIOSDeviceLaunchCertificateGate()
    try testDevicePreflightMarksReadyIOSDeviceLaunchCertificate()
    try testDevicePreflightShowsIOSDeviceLaunchCertificateConsentGate()
    try testDevicePreflightRedactsUnsafeIOSDeviceLaunchCertificate()
    try testDevicePreflightWaitsForMissingFinalClosurePacket()
    try testDevicePreflightBlocksOnFinalClosurePacketFirstBlocker()
    try testDevicePreflightMarksReadyFinalClosurePacket()
    try testDevicePreflightShowsConfiguredEvidenceClosureSection()
    try testDevicePreflightRedactsUnsafeFinalClosurePacket()
    try testDevicePreflightWaitsForMissingFinalOperatorHandoff()
    try testDevicePreflightBlocksOnFinalOperatorHandoffNextAction()
    try testDevicePreflightMarksReadyFinalOperatorHandoff()
    try testDevicePreflightShowsLiveFinalOperatorHandoffConsent()
    try testDevicePreflightRedactsUnsafeFinalOperatorHandoff()
    try testDevicePreflightBlocksAndRedactsFinalLaunchError()
    try testFinalLaunchMobileSummaryWaitsForMissingReport()
    try testFinalLaunchMobileSummaryWaitsWithLaunchReceipt()
    try testFinalLaunchMobileSummaryShowsAcceptanceBlockerReceipt()
    try testFinalLaunchMobileSummaryShowsResourceBlockerReceipt()
    try testFinalLaunchMobileSummaryUsesTopLevelFirstBlockerReceipt()
    try testFinalLaunchMobileSummaryShowsFinalDemoLaunchNextAction()
    try testFinalLaunchMobileSummaryShowsReadyConfiguredReceipt()
    try testFinalLaunchMobileSummaryRedactsUnsafeLaunchReceipt()
    try testLiveProviderConsentSummaryWaitsForProviderReadiness()
    try testLiveProviderConsentSummaryBlocksMissingConfiguredProviders()
    try testLiveProviderConsentSummaryShowsReadyConfiguredConsent()
    try testLiveProviderConsentSummaryShowsReadyLiveEvidence()
    try testLiveProviderConsentSummaryShowsConfiguredBundleRow()
    try testLiveProviderConsentSummaryBlocksConfiguredAcceptanceWithoutBundle()
    try testLiveProviderConsentSummaryBlocksMissingLiveEvidence()
    try testLiveProviderConsentSummaryRedactsUnsafeLiveEvidenceBlocker()
    try testLiveProviderConsentSummaryRedactsUnsafeText()
    try testFinalLaunchMobileSummaryBuildsPartialOperatorStatus()
    try testDecodesFinalDemoLaunchTopLevelStatus()
    try testFinalLaunchMobileSummaryPrefersTopLevelStatus()
    try testFinalLaunchMobileSummaryFallsBackToOverallStatus()
    try testDecodesFinalResourcesPreflightItemsFromFinalLaunchPayload()
    try testDecodesFinalResourceAutoBackendURLHandoffFields()
    try testFinalLaunchMobileSummaryShowsMissingResourceChecklist()
    try testFinalLaunchMobileSummaryShowsReadyResourceChecklist()
    try testFinalLaunchMobileSummaryShowsAutoBackendURLHandoff()
    try testFinalLaunchMobileSummaryRedactsUnsafeResourceChecklist()
    try testDecodesFinalResourceRequirementsFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsBlockedResourceRequirements()
    try testFinalLaunchMobileSummaryShowsResourceRequirementsNextAction()
    try testDecodesFinalResourceFillGuideFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsResourceFillGuide()
    try testDecodesFinalResourceApplyPreviewFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsResourceApplyPreview()
    try testDecodesFinalExternalActionLedgerFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsExternalActionLedger()
    try testFinalLaunchMobileSummaryRedactsUnsafeExternalActionLedger()
    try testDecodesFinalLaunchClosurePacketFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsFinalLaunchClosurePacket()
    try testFinalLaunchMobileSummaryRedactsUnsafeFinalLaunchClosurePacket()
    try testDecodesResourceHandoffFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsMissingResourceHandoff()
    try testFinalLaunchMobileSummaryShowsReadyResourceHandoff()
    try testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff()
    try testDecodesFinalAcceptanceReadinessFromFinalLaunchPayload()
    try testDecodesFinalAcceptanceFreshnessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryWaitsForFinalAcceptanceReadiness()
    try testFinalLaunchMobileSummaryShowsStaleFinalAcceptanceFreshness()
    try testFinalLaunchMobileSummaryShowsBlockedFinalAcceptance()
    try testFinalLaunchMobileSummaryShowsReadyFinalAcceptance()
    try testFinalLaunchMobileSummaryPrioritizesConfiguredAcceptanceCommand()
    try testDecodesThreeDEvaluationReadinessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsReadyThreeDEvaluation()
    try testFinalLaunchMobileSummaryShowsBlockedThreeDEvaluation()
    try testDecodesVisualRegressionReadinessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsReadyVisualRegression()
    try testFinalLaunchMobileSummaryShowsBlockedVisualRegression()
    try testFinalLaunchMobileSummaryShowsStaleVisualRegressionFreshness()
    try testFinalLaunchMobileSummaryRedactsUnsafeVisualRegression()
    try testDecodesLocalShowcaseSmokeFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsLocalShowcaseSmoke()
    try testFinalLaunchMobileSummaryRedactsUnsafeLocalShowcaseSmoke()
    try testDecodesLiveProviderEvidenceFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsReadyLiveProviderEvidence()
    try testFinalLaunchMobileSummaryShowsMissingLiveProviderEvidence()
    try testFinalLaunchMobileSummaryShowsBlockedLiveProviderEvidence()
    try testFinalLaunchMobileSummaryRedactsUnsafeLiveProviderEvidence()
    try testDecodesConfiguredEvidencePlanFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsConfiguredEvidencePlan()
    try testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidencePlan()
    try testDecodesConfiguredEvidenceBundleFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsConfiguredEvidenceBundle()
    try testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidenceBundle()
    try testDecodesPrintFulfillmentReadinessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsPrintFulfillmentReadiness()
    try testFinalLaunchMobileSummaryRedactsUnsafePrintFulfillmentReadiness()
    try testDecodesFinalShowcaseReadinessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsFinalShowcaseReadiness()
    try testFinalLaunchMobileSummaryShowsFinalShowcaseNextAction()
    try testFinalLaunchMobileSummaryShowsPriorityFinalShowcaseActions()
    try testFinalLaunchMobileSummaryShowsFinalShowcaseDeviceActionBundle()
    try testFinalLaunchMobileSummaryRedactsUnsafeFinalShowcaseReadiness()
    try testDecodesNPCAgentEvaluationReadinessFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsReadyNPCAgentEvaluation()
    try testFinalLaunchMobileSummaryShowsBlockedNPCAgentEvaluation()
    try testDecodesFinalOperatorHandoffFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsHandoffNextActions()
    try testFinalLaunchMobileSummaryShowsReadyHandoff()
    try testDecodesIOSDeployRunbookFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook()
    try testFinalLaunchMobileSummaryShowsThreeDEvaluationIOSDeployRunbookSlot()
    try testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook()
    try testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook()
    try testDecodesIOSDeviceEvidenceBundleFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsIOSDeviceEvidenceBundle()
    try testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceEvidenceBundle()
    try testDecodesIOSDeviceLaunchRehearsalReadinessFromFinalLaunchPayload()
    try testDecodesIOSDeviceLaunchRehearsalFreshnessFromFinalLaunchPayload()
    try testDecodesIOSDeviceLaunchRehearsalSourceFreshnessFromFinalLaunchPayload()
    try testDecodesIOSDeviceLaunchCertificateFromFinalLaunchPayload()
    try testFinalLaunchMobileSummaryShowsBlockedIOSDeviceLaunchRehearsal()
    try testFinalLaunchMobileSummaryShowsMultipleIOSDeviceLaunchRehearsalActions()
    try testFinalLaunchMobileSummaryShowsReadyIOSDeviceLaunchRehearsal()
    try testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalFreshness()
    try testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalSourceFreshness()
    try testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceLaunchRehearsal()
    try testFinalLaunchMobileSummaryMarksReadyReport()
    try testFinalLaunchMobileSummaryRedactsUnsafeReportText()
    try testFinalLaunchMobileSummaryRedactsUnsafeAcceptanceText()
    try testFinalLaunchMobileSummaryRedactsUnsafeHandoffText()
    try testFinalLaunchModeDefaultsToLocalForUnsafeValues()
    try testFinalLaunchMobileSummaryShowsLocalModePolicy()
    try testFinalLaunchMobileSummaryShowsConfiguredModePolicy()
    try testDevicePreflightMarksLocalDemoReady()
    try testDevicePreflightMarksSavedNPCHistoryReady()
    try testDemoScriptStartsWithCapture()
    try testDemoScriptMovesToForgeWhenMediaReady()
    try testDemoScriptMarksLocalDemoLoopReady()
    try testDemoScriptBlocksOnProviderReadinessError()
    try testDemoScriptRedactsUnsafeDetail()
    try testDemoScriptShowsBlockedFinalLaunch()
    try testDemoScriptFinalLaunchDetailUsesReceiptFirstBlocker()
    try testDemoScriptCompletesWithReadyFinalLaunch()
    try testDemoScriptRedactsUnsafeFinalLaunchDetail()
    try testDemoScriptShowsReadyThreeDEvaluationBeforeNPCEvaluation()
    try testDemoScriptWaitsForMissingThreeDEvaluation()
    try testDemoScriptBlocksAndRedactsFailedThreeDEvaluation()
    try testDemoScriptShowsReadyNPCEvaluationBeforeFinalLaunch()
    try testDemoScriptWaitsForMissingNPCEvaluation()
    try testDemoScriptBlocksAndRedactsFailedNPCEvaluation()
    try testShowcaseAutopilotBlocksUntilCaptureReady()
    try testShowcaseAutopilotPlansForgeWhenCaptureReady()
    try testShowcaseAutopilotPlansBackendAutonomyForReadySession()
    try testShowcaseAutopilotPlansLegacyTickAdvanceForLegacySession()
    try testShowcaseAutopilotPlansPrintQuoteAfterNPCAutonomy()
    try testShowcaseAutopilotCompletesWhenQuoteAndResourcesReady()
    try testShowcaseAutopilotBlocksOnFinalLaunchBlocker()
    try testShowcaseAutopilotCompletesWhenFinalLaunchReady()
    try testShowcaseAutopilotWaitsForMissingThreeDEvaluation()
    try testShowcaseAutopilotBlocksOnFailedThreeDEvaluation()
    try testShowcaseAutopilotWaitsForMissingNPCEvaluation()
    try testShowcaseAutopilotBlocksOnFailedNPCEvaluation()
    try testShowcaseAutopilotDisablesWhileBusy()
    try testShowcaseAutopilotRedactsUnsafeText()
    try testEncodesPrintQuoteRequestAsSnakeCase()
    try testCaptureIDValidation()
    try testMythSessionIDValidation()
    try testDemoRunSnapshotBuildsFromBackendHistory()
    try testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths()
    try testMultipartBuilderSanitizesHeaderValues()
    try await testUploadObjectCaptureBuildsMultipartRequest()
    try await testCreateMythSessionFromCaptureBuildsJSONRequest()
    try await testInvalidCaptureIDFailsBeforeNetwork()
    try await testHTTPStatusErrorIncludesStatusAndBody()
    try await testHTTPStatusErrorSanitizesSecretsAndTruncatesBody()
    try await testGetBackendHealthBuildsGETRequest()
    try await testGetProviderReadinessBuildsGETRequest()
    try await testGetProviderReadinessSanitizesHTTPErrorBody()
    try testDecodesFinalDemoLaunchPayload()
    try testDecodesConfiguredFinalDemoLaunchPayloadCommands()
    try await testGetFinalDemoLaunchBuildsGETRequest()
    try await testGetConfiguredFinalDemoLaunchBuildsGETRequest()
    try await testGetFinalDemoLaunchRejectsInvalidModeBeforeNetwork()
    try await testCreatePrintQuoteBuildsJSONRequest()
    try await testCreatePrintQuoteSanitizesCheckoutHTTPErrorBody()
    try await testGetMythSessionBuildsGETRequest()
    try await testGetMythSessionHistoryBuildsGETRequest()
    try await testAdvanceMythSessionHistoryBuildsPOSTRequest()
    try await testAdvanceMythSessionHistoryRejectsInvalidIDBeforeNetwork()
    try await testRunMythSessionAutonomyBuildsPOSTRequest()
    try await testRunMythSessionAutonomyRejectsInvalidIDBeforeNetwork()
    try await testInvalidMythSessionIDFailsBeforeNetwork()
    try await testCreateNPCAgentTickBuildsJSONRequest()
    try await testCreateNPCAgentTickSanitizesHTTPErrorBody()
    try await testUploadObjectCaptureUsesGeneratedFilenamesWithoutLocalPaths()
    try await testUploadObjectCaptureRejectsUnsafeContentTypeBeforeNetwork()
    try await testUploadObjectCaptureBuildsARKitScanMultipartRequest()
    try testCaptureModeIncludesGuidedScan()
    try testCaptureDraftBuildsSinglePhotoPayload()
    try testCaptureDraftBuildsPhotoSetPayload()
    try testCaptureDraftBuildsARKitScanPayload()
    try testCaptureDraftBuildsGuidedScanPayload()
    try testCaptureDraftRejectsInvalidMedia()
    try testCaptureDraftRejectsInvalidGuidedScanMedia()
    try testCaptureDraftRejectsOversizedMedia()
    try testCaptureMediaSelectionSummarizesSinglePhoto()
    try testCaptureMediaSelectionRequiresPhotoSetCount()
    try testCaptureMediaSelectionBuildsARKitDraft()
    try testCaptureMediaSelectionSummarizesGuidedScan()
    try testCaptureMediaSelectionClearsWhenModeChanges()
    try testCameraCaptureMediaBuilderBuildsReadySinglePhotoSelection()
    try testGuidedScanPhotoSetBuilderBuildsSortedImageDrafts()
    try testGuidedScanPhotoSetBuilderTruncatesToTwelveImages()
    try testGuidedScanPhotoSetBuilderRejectsTooFewImages()
    try testGuidedScanPhotoSetBuilderRejectsUnsupportedContentType()
    try testGuidedScanPhotoSetBuilderRejectsOversizedMedia()
    try testARKitScanPackageBuilderBuildsReadySelection()
    try testARKitScanPackageBuilderNormalizesAndSortsReferences()
    try testARKitScanPackageBuilderTruncatesReferencesToEleven()
    try testARKitScanPackageBuilderRejectsUnsupportedScan()
    try testARKitScanPackageBuilderRejectsUnsupportedReference()
    try testARKitScanPackageBuilderRejectsOversizedScan()
    try testARKitScanPackageBuilderRejectsOversizedReference()
    try testCaptureGenerationReadinessWaitsForGuidedScanPhotos()
    try testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute()
    try testCaptureGenerationReadinessMarksARKitScanAssetRoute()
    try testCaptureGenerationReadinessMarksMissingThreeDProvider()
    try testCaptureGenerationReadinessRedactsProviderErrors()
    try testThreeDGenerationInputReviewWaitsForCaptureMedia()
    try testThreeDGenerationInputReviewShowsGuidedScanProviderSelection()
    try testThreeDGenerationInputReviewShowsARKitScanPackage()
    try testThreeDGenerationInputReviewShowsMeshyReadyRoute()
    try testThreeDGenerationInputReviewRedactsUnsafeText()
    try testCaptureGenerationReceiptWaitsBeforeCapture()
    try testCaptureGenerationReceiptShowsUploadedCaptureBeforeSession()
    try testCaptureGenerationReceiptShowsReadyGuidedScanGeneration()
    try testCaptureGenerationReceiptFlagsMissingProvenance()
    try testCaptureGenerationReceiptRedactsUnsafeText()
    try testForgeProgressReceiptWaitsBeforeForge()
    try testForgeProgressReceiptShowsCaptureUploadRunning()
    try testForgeProgressReceiptShowsMythSessionRunningAfterCaptureUpload()
    try testForgeProgressReceiptShowsReadyProviderAndNPCRuntime()
    try testForgeProgressReceiptRedactsUnsafeFailure()
    try testGenerationResultReceiptWaitsForForge()
    try testGenerationResultReceiptShowsCompleteForgeResult()
    try testGenerationResultReceiptRequiresIOSSceneVariant()
    try testGenerationResultReceiptRedactsUnsafeText()
    try testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset()
    try testArtifactGenerationProvenanceSummaryShowsMultiImageRoute()
    try testArtifactGenerationProvenanceSummaryShowsScanAssets()
    try testArtifactGenerationProvenanceSummaryWaitsForMissingProvenance()
    try testArtifactGenerationProvenanceSummaryRedactsUnsafeText()
    try testArtifactPreviewStateMarksLocalUSDZAsSceneLoadable()
    try testArtifactPreviewStateHandlesMissingURI()
    try testArtifactPreviewStateHandlesMissingFormat()
    try await testArtifactAssetPreparerUsesLocalSceneURL()
    try await testArtifactAssetPreparerDownloadsRemoteUSDZForSceneKit()
    try await testArtifactAssetPreparerDownloadsRemoteDAEForLocalBackendScene()
    try await testArtifactAssetPreparerCachesRemoteGLBButRequiresConversion()
    try await testArtifactAssetPreparerPrefersSceneVariantOverPrimaryGLB()
    try await testArtifactAssetPreparerReportsLocalSceneVariantSourceURI()
    try await testArtifactAssetPreparerRejectsInvalidRemoteURI()
    try await testArtifactAssetPreparerSkipsDownloadWhenFormatMissing()
    try await testArtifactAssetPreparerTreatsCancellationAsCancelled()
    try testArtifactSceneLoadProofWaitsForPreparedAsset()
    try testArtifactSceneLoadProofMarksLoadedScene()
    try testArtifactSceneLoadProofMarksConversionRequired()
    try testArtifactSceneLoadProofRedactsFailedSceneLoad()
    try testArtifactHandoffActionsWaitForSession()
    try testArtifactHandoffActionsOpenAndShareSceneAsset()
    try testArtifactHandoffActionsShareCachedGLBNeedsConversion()
    try testArtifactHandoffActionsOfferRetryAfterDownloadFailure()
    try testArtifactHandoffActionsOfferRetryAfterSceneLoadFailure()
    try testArtifactHandoffActionsRedactUnsafeDetails()
    try testForgeFlowReducerTransitionsThroughReadyAndReset()
    try await testForgeFlowServiceUploadsCaptureThenCreatesSession()
    try await testForgeFlowServiceStopsBeforeSessionWhenUploadFails()
    try await testForgeFlowServiceRejectsInvalidDraftBeforeNetwork()
    try testSwiftUIScaffoldIncludesWorldResolution()
    print("PersonalMythForgeMobileCoreContractTests passed")
} catch {
    fputs("Contract test failed: \(error)\n", stderr)
    exit(1)
}

private func testDecodesObjectCaptureFixture() throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")

    try expectEqual(capture.captureId, "cap_ba02a3816bd145b4")
    try expectEqual(capture.mediaItems.first?.uri, "local-capture://cap_ba02a3816bd145b4/media_0.jpg")
    try expectEqual(capture.objectObservation.label, "old brass key")
}

private func testDecodesMythSessionFixture() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    try expectEqual(session.status, "ready_for_review")
    try expectEqual(session.objectCard.label, "old brass key")
    try expectEqual(session.npcReactions.count, 3)
    try expectEqual(session.npcAgentRuntime, "local_agent_runtime")
    try expectEqual(session.npcAgentTraces.count, 3)
    try expectEqual(session.npcAgentTraces[0].npcId, "npc_archivist")
    try expectEqual(session.npcAgentTraces[0].belief, "The key belongs to a door that remembers who knocked.")
    try expectEqual(session.npcAgentTraces[0].proposedAction, "catalog the key")
    try expectEqual(session.npcAgentTraces[0].confidence, 0.81)
    try expectEqual(session.worldResolution.acceptedActions.count, 2)
    try expectEqual(session.generatedAsset.variants.count, 2)
    try expectEqual(session.generatedAsset.variants[0].role, "game_asset")
    try expectEqual(session.generatedAsset.variants[0].format, "glb")
    try expectEqual(session.generatedAsset.variants[1].role, "ios_scene_asset")
    try expectEqual(session.generatedAsset.variants[1].format, "dae")
    try expectEqual(
        session.generatedAsset.variants[1].uri,
        "http://192.168.1.10:8080/v1/generated-assets/myth_0123456789abcdef/scene.dae"
    )
    try expectTrue(session.generatedAsset.variants[1].isSceneLoadable)
    let provenance = try require(
        session.generatedAsset.generationProvenance,
        "expected generated asset provenance"
    )
    try expectEqual(provenance.inputMode, "multi_image")
    try expectEqual(provenance.providerRoute, "/openapi/v1/multi-image-to-3d")
    try expectEqual(provenance.sourceImageCount, 3)
    try expectEqual(provenance.selectedSourceImageCount, 3)
    try expectEqual(provenance.sourceAssetCount, 0)
    try expectEqual(provenance.maxSourceImages, 4)
    try expectFalse(provenance.rawSourcesIncluded)
    try expectEqual(session.printCandidate.requiresUserApproval, true)
}

private func testDecodesMythSessionWithoutGeneratedAssetVariants() throws {
    var payload = try require(
        try JSONSerialization.jsonObject(with: FixtureLoader.data(from: "myth-session-response")) as? [String: Any],
        "expected myth session fixture object"
    )
    var generatedAsset = try require(
        payload["generated_asset"] as? [String: Any],
        "expected generated asset object"
    )
    generatedAsset.removeValue(forKey: "variants")
    payload["generated_asset"] = generatedAsset

    let data = try JSONSerialization.data(withJSONObject: payload)
    let session = try PMFJSON.decoder.decode(MythSession.self, from: data)

    try expectEqual(session.generatedAsset.variants, [])
}

private func testDecodesMythSessionWithoutGenerationProvenance() throws {
    var payload = try require(
        try JSONSerialization.jsonObject(with: FixtureLoader.data(from: "myth-session-response")) as? [String: Any],
        "expected myth session fixture object"
    )
    var generatedAsset = try require(
        payload["generated_asset"] as? [String: Any],
        "expected generated asset object"
    )
    generatedAsset.removeValue(forKey: "generation_provenance")
    payload["generated_asset"] = generatedAsset

    let data = try JSONSerialization.data(withJSONObject: payload)
    let session = try PMFJSON.decoder.decode(MythSession.self, from: data)

    if session.generatedAsset.generationProvenance != nil {
        throw ContractTestError.expectationFailed("Expected missing generation provenance to decode as nil")
    }
}

private func testDecodesMythSessionWithoutNPCAgentTraceFields() throws {
    var payload = try require(
        try JSONSerialization.jsonObject(with: FixtureLoader.data(from: "myth-session-response")) as? [String: Any],
        "expected myth session fixture object"
    )
    payload.removeValue(forKey: "npc_agent_runtime")
    payload.removeValue(forKey: "npc_agent_traces")

    let data = try JSONSerialization.data(withJSONObject: payload)
    let session = try PMFJSON.decoder.decode(MythSession.self, from: data)

    try expectEqual(session.npcAgentRuntime, "")
    try expectEqual(session.npcAgentTraces, [])
}

private func testDecodesNPCAgentTickPayload() throws {
    let data = Data(
        """
        {
          "session_id": "myth_0123456789abcdef",
          "tick_index": 1,
          "agent_runtime": "local_tick_runtime",
          "npc_agent_traces": [
            {
              "npc_id": "mara",
              "name": "Mara",
              "belief": "The relic is becoming a public promise.",
              "intention": "turn awe into shared witness",
              "proposed_action": "invite_neighbors_to_witness",
              "rationale": "Mara reacts to 1 recent village event.",
              "confidence": 0.82
            }
          ],
          "npc_reactions": [
            {
              "npc_id": "mara",
              "name": "Mara",
              "emotion": "awe",
              "interpretation": "The relic is becoming a public promise.",
              "plan": ["invite_neighbors_to_witness"],
              "world_change": "faith_in_player_increases"
            }
          ],
          "world_resolution": {
            "arbitrator": "local_rules",
            "summary": "The village accepts 1 ritual actions around the relic.",
            "accepted_actions": [
              {
                "npc_id": "mara",
                "action": "invite_neighbors_to_witness",
                "status": "accepted",
                "reason": "safe ritual or debate action"
              }
            ],
            "rejected_actions": [],
            "world_state_delta": {
              "faith": 1,
              "artifact_renown": 1
            },
            "visible_changes": ["Mara prepares to invite neighbors to witness."]
          }
        }
        """.utf8
    )

    let tick = try PMFJSON.decoder.decode(NPCAgentTick.self, from: data)

    try expectEqual(tick.sessionId, "myth_0123456789abcdef")
    try expectEqual(tick.tickIndex, 1)
    try expectEqual(tick.agentRuntime, "local_tick_runtime")
    try expectEqual(tick.npcAgentTraces[0].proposedAction, "invite_neighbors_to_witness")
    try expectEqual(tick.npcReactions[0].emotion, "awe")
    try expectEqual(tick.worldResolution.acceptedActions[0].status, "accepted")
}

private func testDecodesMythSessionHistoryPayload() throws {
    let session = try backendHistorySession()
    let tick = npcTick(sessionId: session.sessionId, tickIndex: 1)
    let payload = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: [tick],
        updatedAt: "2026-06-06T12:00:00+00:00"
    )

    let data = try PMFJSON.encoder.encode(payload)
    let body = String(decoding: data, as: UTF8.self)
    let decoded = try PMFJSON.decoder.decode(MythSessionHistory.self, from: data)

    try expectContains(body, #""session_id":"#)
    try expectContains(body, #""npc_ticks":"#)
    try expectEqual(decoded, payload)
}

private func testDecodesNPCAutonomyRunPayload() throws {
    let session = try backendHistorySession()
    let history = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: [
            npcTick(sessionId: session.sessionId, tickIndex: 1),
            npcTick(sessionId: session.sessionId, tickIndex: 2),
            npcTick(sessionId: session.sessionId, tickIndex: 3),
        ],
        updatedAt: "2026-06-06T12:10:00+00:00"
    )
    let run = NPCAutonomyRun(
        sessionId: session.sessionId,
        requestedSteps: 3,
        completedSteps: 3,
        startedTickIndex: 1,
        completedTickIndex: 3,
        agentRuntime: "local_tick_runtime",
        history: history
    )

    let data = try PMFJSON.encoder.encode(run)
    let body = String(decoding: data, as: UTF8.self)
    let decoded = try PMFJSON.decoder.decode(NPCAutonomyRun.self, from: data)

    try expectContains(body, #""requested_steps":"#)
    try expectContains(body, #""completed_tick_index":"#)
    try expectEqual(decoded, run)
}

private func testNPCRitualSceneBuildsThreeActorsFromSession() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    let scene = NPCRitualSceneBuilder.build(session: session, latestTick: nil)

    try expectEqual(scene.title, session.mythSeed.title)
    try expectEqual(scene.runtime, session.npcAgentRuntime)
    try expectEqual(scene.actors.count, 3)
    try expectEqual(scene.actors.map(\.npcId), ["npc_archivist", "npc_smith", "npc_child"])
    try expectEqual(scene.actors[0].positionX, -1.1)
    try expectEqual(scene.actors[0].positionZ, 0.7)
    try expectEqual(scene.actors[1].positionX, 1.1)
    try expectEqual(scene.actors[2].positionZ, -1.05)
    try expectEqual(scene.actors[0].stance, .acting)
    try expectEqual(scene.actors[1].stance, .debating)
    try expectContains(scene.actors[0].action, "catalog")
    try expectEqual(scene.visibleChanges, session.worldResolution.visibleChanges)
}

private func testNPCRitualSceneUsesLatestTickActions() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let tick = ritualTick(sessionId: session.sessionId, tickIndex: 2)

    let scene = NPCRitualSceneBuilder.build(session: session, latestTick: tick)

    try expectEqual(scene.runtime, "local_tick_runtime")
    try expectEqual(scene.visibleChanges, tick.worldResolution.visibleChanges)
    try expectEqual(scene.actors.map(\.npcId), ["mara", "ior", "senn"])
    try expectEqual(scene.actors[0].stance, .acting)
    try expectEqual(scene.actors[1].stance, .debating)
    try expectEqual(scene.actors[2].stance, .watching)
    try expectContains(scene.actors[0].action, "invite neighbors")
    try expectContains(scene.actors[1].action, "argue about")
}

private func testNPCRitualSceneBackfillsSparseLatestTick() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let tick = npcTick(sessionId: session.sessionId, tickIndex: 4)

    let scene = NPCRitualSceneBuilder.build(session: session, latestTick: tick)

    try expectEqual(scene.actors.count, 3)
    try expectEqual(scene.actors.map(\.npcId), ["mara", "npc_archivist", "npc_smith"])
    try expectEqual(scene.actors[0].stance, .acting)
    try expectContains(scene.actors[0].action, "move closer")
    try expectContains(scene.actors[1].action, "catalog")
}

private func testNPCRitualSceneRedactsUnsafeText() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let tick = ritualTick(
        sessionId: session.sessionId,
        tickIndex: 3,
        unsafeSuffix: " sk-test /Users/zhexu/private file:///tmp/private local-capture://cap/media checkout_url"
    )

    let scene = NPCRitualSceneBuilder.build(session: session, latestTick: tick)
    let data = try PMFJSON.encoder.encode(scene)
    let text = try require(String(data: data, encoding: .utf8), "expected encoded ritual scene text")

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
}

private func testDemoRunSnapshotKeepsMatchingTicksSortedAndBounded() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let ticks = (0..<16).map { index in
        npcTick(sessionId: index == 3 ? "other_session" : session.sessionId, tickIndex: index)
    }.reversed()

    let snapshot = DemoRunSnapshot(savedAt: "2026-06-06T12:00:00Z", session: session, npcTicks: Array(ticks))

    try expectEqual(snapshot.schemaVersion, DemoRunSnapshot.currentSchemaVersion)
    try expectEqual(snapshot.npcTicks.count, DemoRunSnapshot.maximumStoredTicks)
    try expectEqual(snapshot.npcTicks.map(\.sessionId).filter { $0 != session.sessionId }, [])
    try expectEqual(snapshot.npcTicks.map(\.tickIndex), Array(4...15))
    try expectEqual(snapshot.latestTick?.tickIndex, 15)
}

private func testDemoRunSnapshotBuildsFromBackendHistory() throws {
    let session = try backendHistorySession()
    let ticks = (1...18).map { index in
        npcTick(sessionId: index == 3 ? "other_session" : session.sessionId, tickIndex: index)
    }.reversed()
    let history = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: Array(ticks),
        updatedAt: "2026-06-06T12:00:00+00:00"
    )

    let snapshot = DemoRunSnapshot(history: history, savedAt: "2026-06-06T12:01:00Z")

    try expectEqual(snapshot.savedAt, "2026-06-06T12:01:00Z")
    try expectEqual(snapshot.session, session)
    try expectEqual(snapshot.npcTicks.count, DemoRunSnapshot.maximumStoredTicks)
    try expectEqual(snapshot.npcTicks.map(\.sessionId).filter { $0 != session.sessionId }, [])
    try expectEqual(snapshot.npcTicks.map(\.tickIndex), Array(7...18))
}

private func testDemoRunSnapshotEncodesSnakeCaseJSONWithoutRawMediaOrSecrets() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let snapshot = DemoRunSnapshot(
        savedAt: "2026-06-06T12:00:00Z",
        session: session,
        npcTicks: [npcTick(sessionId: session.sessionId, tickIndex: 1)]
    )

    let data = try PMFJSON.encoder.encode(snapshot)
    let body = String(decoding: data, as: UTF8.self)

    try expectContains(body, #""schema_version":1"#)
    try expectContains(body, #""npc_ticks":"#)
    try expectNotContains(body, "raw-photo-bytes")
    try expectNotContains(body, "Authorization=Bearer")
    try expectNotContains(body, "api_key=")
    try expectNotContains(body, "file:///")

    let decoded = try PMFJSON.decoder.decode(DemoRunSnapshot.self, from: data)
    try expectEqual(decoded, snapshot)
}

private func testDemoRunSnapshotFileStoreSavesLoadsOverwritesAndClears() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let temporaryDirectory = FileManager.default.temporaryDirectory
        .appendingPathComponent("pmf-demo-snapshot-\(UUID().uuidString)", isDirectory: true)
    let store = DemoRunSnapshotFileStore(
        snapshotURL: temporaryDirectory.appendingPathComponent("demo-run-snapshot.json")
    )
    defer {
        try? FileManager.default.removeItem(at: temporaryDirectory)
    }

    try expectTrue(try store.load() == nil)

    let first = DemoRunSnapshot(savedAt: "2026-06-06T12:00:00Z", session: session)
    try store.save(first)
    try expectEqual(try store.load(), first)

    let second = first.appending(
        npcTick(sessionId: session.sessionId, tickIndex: 1),
        savedAt: "2026-06-06T12:01:00Z"
    )
    try store.save(second)
    try expectEqual(try store.load(), second)

    try store.clear()
    try expectTrue(try store.load() == nil)
}

private func testDecodesProviderReadinessPayload() throws {
    let data = Data(
        """
        {
          "overall_demo_ready": true,
          "overall_real_ready": false,
          "providers": [
            {
              "kind": "three_d",
              "selected_provider": "local",
              "status": "local_stub",
              "is_demo_ready": true,
              "is_real_provider_ready": false,
              "missing_env": [],
              "capabilities": ["text_to_3d_stub"],
              "notes": ["Local 3D provider is deterministic."]
            },
            {
              "kind": "npc",
              "selected_provider": "openai",
              "status": "missing_configuration",
              "is_demo_ready": false,
              "is_real_provider_ready": false,
              "missing_env": ["OPENAI_API_KEY"],
              "capabilities": ["structured_agent_traces"],
              "notes": ["OPENAI_API_KEY is required."]
            }
          ]
        }
        """.utf8
    )

    let readiness = try PMFJSON.decoder.decode(ProviderReadinessResponse.self, from: data)

    try expectTrue(readiness.overallDemoReady)
    try expectFalse(readiness.overallRealReady)
    try expectEqual(readiness.providers.count, 2)
    try expectEqual(readiness.providers[0].kind, "three_d")
    try expectEqual(readiness.providers[0].status, "local_stub")
    try expectTrue(readiness.providers[0].isDemoReady)
    try expectFalse(readiness.providers[0].isRealProviderReady)
    try expectEqual(readiness.providers[1].missingEnv, ["OPENAI_API_KEY"])
}

private func testNPCAgentModeWaitsForSession() throws {
    let summary = NPCAgentModeSummaryBuilder.build(
        session: nil,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: nil,
        providerReadinessError: nil
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.title, "NPC agents waiting")
    try expectEqual(summary.providerLabel, "unknown")
    try expectEqual(summary.runtimeLabel, "not started")
    try expectEqual(summary.traceCount, 0)
    try expectEqual(summary.tickHistoryCount, 0)
}

private func testNPCAgentModeShowsLocalDemoRuntime() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]

    let summary = NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.status, .localDemo)
    try expectEqual(summary.title, "Local NPC agent mode")
    try expectEqual(summary.providerLabel, "local")
    try expectEqual(summary.runtimeLabel, "local_agent_runtime")
    try expectEqual(summary.traceCount, 1)
    try expectContains(summary.detail, "deterministic")
}

private func testNPCAgentModeShowsOpenAIReadyRuntime() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcDirector = "openai"
    session.npcAgentRuntime = "openai_structured_runtime"
    session.npcAgentTraces = [
        sampleNPCAgentTrace(npcId: "mara"),
        sampleNPCAgentTrace(npcId: "ior"),
        sampleNPCAgentTrace(npcId: "senn"),
    ]

    let summary = NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 2,
        providerReadiness: openAINPCProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.status, .aiReady)
    try expectEqual(summary.title, "OpenAI NPC Agent ready")
    try expectEqual(summary.providerLabel, "openai")
    try expectEqual(summary.runtimeLabel, "openai_structured_runtime")
    try expectEqual(summary.traceCount, 3)
    try expectEqual(summary.tickHistoryCount, 2)
    try expectEqual(summary.missingEnv, [])
}

private func testNPCAgentModeShowsMissingOpenAIKey() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcDirector = "openai"
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]

    let summary = NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: missingOpenAINPCProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.status, .needsSetup)
    try expectEqual(summary.title, "NPC Agent setup needed")
    try expectEqual(summary.providerLabel, "openai")
    try expectEqual(summary.missingEnv, ["OPENAI_API_KEY"])
    try expectContains(summary.detail, "OPENAI_API_KEY")
}

private func testNPCAgentModeUsesLatestTickRuntime() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]
    var tick = npcTick(sessionId: session.sessionId, tickIndex: 3)
    tick.agentRuntime = "openai_tick_structured_runtime"
    tick.npcAgentTraces = [
        sampleNPCAgentTrace(npcId: "mara"),
        sampleNPCAgentTrace(npcId: "ior"),
    ]

    let summary = NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: tick,
        tickHistoryCount: 3,
        providerReadiness: openAINPCProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.status, .aiReady)
    try expectEqual(summary.runtimeLabel, "openai_tick_structured_runtime")
    try expectEqual(summary.traceCount, 2)
    try expectEqual(summary.tickHistoryCount, 3)
}

private func testNPCAgentModeRedactsUnsafeText() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcDirector = "openai sk-test /Users/zhexu checkout_url"
    session.npcAgentRuntime = "Bearer token file:///tmp/private"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]

    let summary = NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: ProviderReadinessResponse(
            overallDemoReady: false,
            overallRealReady: false,
            providers: [
                ProviderReadinessItem(
                    kind: "npc",
                    selectedProvider: "openai sk-test",
                    status: "Authorization Bearer token /Users/zhexu",
                    isDemoReady: false,
                    isRealProviderReady: false,
                    missingEnv: ["OPENAI_API_KEY", "sk-test"],
                    notes: ["checkout_url file:///tmp/private"]
                ),
            ]
        ),
        providerReadinessError: "Authorization Bearer token sk-test /Users/zhexu checkout_url file:///tmp/private"
    )
    let text = (
        [
            summary.title,
            summary.detail,
            summary.providerLabel,
            summary.runtimeLabel,
        ]
        + summary.missingEnv
        + summary.privacyNotes
    ).joined(separator: " ")

    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
    try expectNotContains(text, "checkout_url")
    try expectNotContains(text, "file:///")
}

private func testNPCAgentTickSummaryWaitsBeforeSession() throws {
    let summary = NPCAgentTickSummaryBuilder.build(
        session: nil,
        latestTick: nil,
        tickHistoryCount: 0,
        isAdvancingTick: false,
        isRunningAutonomy: false,
        errorMessage: nil
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.tickLabel, "not started")
    try expectEqual(summary.runtimeLabel, "not started")
    try expectContains(summary.detail, "Forge")
    try expectContains(summary.privacyNotes.joined(separator: " "), "approved myth session")
}

private func testNPCAgentTickSummaryShowsInitialSessionTraces() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [
        sampleNPCAgentTrace(npcId: "mara"),
        sampleNPCAgentTrace(npcId: "ior"),
        sampleNPCAgentTrace(npcId: "senn"),
    ]

    let summary = NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        isAdvancingTick: false,
        isRunningAutonomy: false,
        errorMessage: nil
    )

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.tickLabel, "initial")
    try expectEqual(summary.runtimeLabel, "local_agent_runtime")
    try expectContains(summary.title, "Initial NPC Agent traces")
    try expectContains(summary.decisionLabel, "3 initial traces")
    try expectContains(summary.rows.joined(separator: " "), "Saved ticks: 0")
}

private func testNPCAgentTickSummaryShowsLatestTickResolution() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    let tick = ritualTick(sessionId: session.sessionId, tickIndex: 2)

    let summary = NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: tick,
        tickHistoryCount: 2,
        isAdvancingTick: false,
        isRunningAutonomy: false,
        errorMessage: nil
    )

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.tickLabel, "tick 2")
    try expectEqual(summary.runtimeLabel, "local_tick_runtime")
    try expectContains(summary.title, "NPC Agent tick resolved")
    try expectContains(summary.decisionLabel, "1 accepted")
    try expectContains(summary.decisionLabel, "1 rejected")
    try expectContains(summary.rows.joined(separator: " "), "Agent traces: 3")
    try expectContains(summary.rows.joined(separator: " "), "Visible changes: 2")
    try expectContains(summary.rows.joined(separator: " "), "Saved ticks: 2")
}

private func testNPCAgentTickSummaryShowsAutonomyRunning() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    let tick = npcTick(sessionId: session.sessionId, tickIndex: 4)

    let summary = NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: tick,
        tickHistoryCount: 4,
        isAdvancingTick: false,
        isRunningAutonomy: true,
        errorMessage: nil
    )

    try expectEqual(summary.status, .running)
    try expectContains(summary.title, "running")
    try expectContains(summary.detail, "3-step")
    try expectEqual(summary.tickLabel, "tick 4")
    try expectEqual(summary.runtimeLabel, "local_tick_runtime")
}

private func testNPCAgentTickSummaryRedactsUnsafeText() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime sk-test /Users/zhexu"
    session.npcAgentTraces = [
        NPCAgentTrace(
            npcId: "mara",
            name: "Mara",
            belief: "sk-test /Users/zhexu/private",
            intention: "Bearer token",
            proposedAction: "open file:///tmp/private",
            rationale: "local-capture://cap/media checkout_url",
            confidence: 0.82
        ),
    ]
    let tick = ritualTick(
        sessionId: session.sessionId,
        tickIndex: 5,
        unsafeSuffix: " sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )

    let summary = NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: tick,
        tickHistoryCount: 5,
        isAdvancingTick: false,
        isRunningAutonomy: false,
        errorMessage: "Authorization Bearer token sk-test /Users/zhexu checkout_url file:///tmp/private"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testNPCAgentActionGateDisablesWithoutSession() throws {
    let gate = NPCAgentActionGateBuilder.build(
        session: nil,
        npcAgentModeSummary: NPCAgentModeSummaryBuilder.build(
            session: nil,
            latestTick: nil,
            tickHistoryCount: 0,
            providerReadiness: nil,
            providerReadinessError: nil
        ),
        npcAgentTickSummary: NPCAgentTickSummaryBuilder.build(
            session: nil,
            latestTick: nil,
            tickHistoryCount: 0,
            isAdvancingTick: false,
            isRunningAutonomy: false,
            errorMessage: nil
        ),
        isAdvancingTick: false,
        isRunningAutonomy: false
    )

    try expectEqual(gate.canAdvanceVillage, false)
    try expectEqual(gate.canRunAutonomy, false)
    try expectEqual(gate.disabledReason, "session_required")
    try expectContains(gate.detail, "Forge")
}

private func testNPCAgentActionGateEnablesLocalDemoActions() throws {
    let session = localAgentSession()
    let gate = NPCAgentActionGateBuilder.build(
        session: session,
        npcAgentModeSummary: localDemoNPCAgentModeSummary(session: session),
        npcAgentTickSummary: npcAgentTickSummary(session: session),
        isAdvancingTick: false,
        isRunningAutonomy: false
    )

    try expectEqual(gate.canAdvanceVillage, true)
    try expectEqual(gate.canRunAutonomy, true)
    try expectEqual(gate.disabledReason, nil)
    try expectContains(gate.detail, "local")
}

private func testNPCAgentActionGateDisablesMissingOpenAISetup() throws {
    let session = localAgentSession()
    let gate = NPCAgentActionGateBuilder.build(
        session: session,
        npcAgentModeSummary: missingOpenAINPCAgentModeSummary(session: session),
        npcAgentTickSummary: npcAgentTickSummary(session: session),
        isAdvancingTick: false,
        isRunningAutonomy: false
    )

    try expectEqual(gate.canAdvanceVillage, false)
    try expectEqual(gate.canRunAutonomy, false)
    try expectEqual(gate.disabledReason, "npc_setup_required")
    try expectContains(gate.detail, "OPENAI_API_KEY")
}

private func testNPCAgentActionGateDisablesWhileAutonomyRuns() throws {
    let session = localAgentSession()
    let gate = NPCAgentActionGateBuilder.build(
        session: session,
        npcAgentModeSummary: localDemoNPCAgentModeSummary(session: session),
        npcAgentTickSummary: npcAgentTickSummary(session: session, isRunningAutonomy: true),
        isAdvancingTick: false,
        isRunningAutonomy: true
    )

    try expectEqual(gate.canAdvanceVillage, false)
    try expectEqual(gate.canRunAutonomy, false)
    try expectEqual(gate.disabledReason, "npc_action_running")
    try expectContains(gate.detail, "Running")
}

private func testNPCAgentActionGateRedactsUnsafeDetail() throws {
    let session = localAgentSession()
    let summary = NPCAgentModeSummary(
        status: .needsSetup,
        title: "NPC setup needed",
        detail: "Authorization Bearer token sk-test /Users/zhexu file:///tmp/private local-capture://cap checkout_url",
        providerLabel: "openai",
        runtimeLabel: "openai",
        traceCount: 1,
        tickHistoryCount: 0,
        missingEnv: ["OPENAI_API_KEY"],
        privacyNotes: []
    )
    let gate = NPCAgentActionGateBuilder.build(
        session: session,
        npcAgentModeSummary: summary,
        npcAgentTickSummary: npcAgentTickSummary(session: session),
        isAdvancingTick: false,
        isRunningAutonomy: false
    )
    let text = String(decoding: try PMFJSON.encoder.encode(gate), as: UTF8.self)

    try expectEqual(gate.canRunAutonomy, false)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
}

private func testDecodesPrintQuotePayload() throws {
    let data = Data(
        """
        {
          "kind": "print_quote",
          "provider": "local_stub",
          "status": "draft_quote",
          "source_asset_uri": "local://generated-assets/myth_test.glb",
          "print_candidate_uri": "local://print-candidates/myth_test.3mf",
          "currency": "USD",
          "estimated_price_cents": 1600,
          "estimated_production_days": 5,
          "estimated_shipping_days": 6,
          "checkout_url": null,
          "requires_user_approval": true,
          "approval_reason": "Draft quote must be reviewed.",
          "quote_notes": ["material=standard_resin", "local quote stub"]
        }
        """.utf8
    )

    let quote = try PMFJSON.decoder.decode(PrintQuote.self, from: data)

    try expectEqual(quote.kind, "print_quote")
    try expectEqual(quote.provider, "local_stub")
    try expectEqual(quote.status, "draft_quote")
    try expectEqual(quote.currency, "USD")
    try expectEqual(quote.estimatedPriceCents, 1600)
    try expectEqual(quote.estimatedProductionDays, 5)
    try expectEqual(quote.estimatedShippingDays, 6)
    try expectEqual(quote.checkoutUrl, nil)
    try expectEqual(quote.requiresUserApproval, true)
    try expectEqual(quote.quoteNotes.count, 2)
}

private func testPrintFulfillmentReceiptWaitsForQuote() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))

    let receipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: nil,
        isLoading: false,
        errorMessage: nil,
        isApproved: false
    )

    try expectEqual(receipt.status, .waiting)
    try expectEqual(receipt.canApprove, false)
    try expectEqual(receipt.canHandOffToProvider, false)
    try expectContains(receipt.title, "Print fulfillment waiting")
    try expectContains(receipt.detail, "quote")
    try expectContains(receipt.row(id: "candidate")?.detail ?? "", "stl")
}

private func testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    let quote = localPrintQuote()

    let receipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: quote,
        isLoading: false,
        errorMessage: nil,
        isApproved: false
    )

    try expectEqual(receipt.status, .needsApproval)
    try expectEqual(receipt.canApprove, true)
    try expectEqual(receipt.canHandOffToProvider, false)
    try expectContains(receipt.title, "Print approval required")
    try expectContains(receipt.row(id: "provider")?.detail ?? "", "local_stub")
    try expectContains(receipt.row(id: "quote")?.detail ?? "", "USD 16.00")
    try expectContains(receipt.row(id: "approval")?.detail ?? "", "review before fulfillment")
}

private func testPrintFulfillmentReceiptShowsApprovedProviderHandoff() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    let quote = localPrintQuote()

    let receipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: quote,
        isLoading: false,
        errorMessage: nil,
        isApproved: true
    )

    try expectEqual(receipt.status, .ready)
    try expectEqual(receipt.canApprove, true)
    try expectEqual(receipt.canHandOffToProvider, true)
    try expectContains(receipt.title, "Print handoff ready")
    try expectContains(receipt.detail, "provider handoff")
    try expectContains(receipt.privacyNotes.joined(separator: " "), "Checkout/payment links stay withheld")
}

private func testPrintFulfillmentReceiptHandlesNoApprovalRequiredQuote() throws {
    let session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    var quote = localPrintQuote()
    quote.requiresUserApproval = false
    quote.approvalReason = "Provider quote can move to handoff without extra review."
    quote.checkoutUrl = "https://checkout.example/pay?token=secret"

    let receipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: quote,
        isLoading: false,
        errorMessage: nil,
        isApproved: false
    )

    try expectEqual(receipt.status, .ready)
    try expectEqual(receipt.canApprove, false)
    try expectEqual(receipt.canHandOffToProvider, true)
    try expectContains(receipt.row(id: "approval")?.detail ?? "", "No extra approval required")

    let text = String(decoding: try PMFJSON.encoder.encode(receipt), as: UTF8.self)
    try expectNotContains(text, "checkout.example")
    try expectNotContains(text, "token=secret")
}

private func testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText() throws {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.printCandidate.approvalReason = "review sk-test /Users/me/private file:///tmp/private local-capture://cap checkout_url=https://pay.example Bearer token"
    var quote = localPrintQuote()
    quote.provider = "treatstock Bearer token"
    quote.checkoutUrl = "https://checkout.example/pay?token=secret"
    quote.approvalReason = "approve after Authorization=Bearer secret"
    quote.quoteNotes = ["safe quote note", "api_key=secret", "private path /tmp/private"]

    let receipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: quote,
        isLoading: false,
        errorMessage: "Provider failed Authorization=Bearer secret api_key=secret checkout_url=https://pay.example /Users/me/raw local-capture://cap",
        isApproved: true
    )
    let text = String(decoding: try PMFJSON.encoder.encode(receipt), as: UTF8.self)

    try expectEqual(receipt.status, .blocked)
    try expectEqual(receipt.canHandOffToProvider, false)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout.example")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key=secret")
}

private func testShowcaseEvidenceWaitsForSession() throws {
    let summary = ShowcaseEvidenceSummaryBuilder.build(
        captureReceipt: CaptureGenerationReceiptBuilder.build(
            capture: nil,
            session: nil,
            captureGenerationReadiness: CaptureGenerationReadinessBuilder.build(
                selection: CaptureMediaSelection(mode: .singlePhoto),
                providerReadiness: nil,
                providerReadinessError: nil
            )
        ),
        generationReceipt: GenerationResultReceiptBuilder.build(session: nil),
        sceneLoadProof: ArtifactSceneLoadProofBuilder.build(preparedAsset: nil, sceneLoadError: nil),
        npcTickSummary: NPCAgentTickSummaryBuilder.build(
            session: nil,
            latestTick: nil,
            tickHistoryCount: 0,
            isAdvancingTick: false,
            isRunningAutonomy: false,
            errorMessage: nil
        ),
        tickHistoryCount: 0,
        printFulfillmentReceipt: PrintFulfillmentReceiptBuilder.build(
            session: nil,
            quote: nil,
            isLoading: false,
            errorMessage: nil,
            isApproved: false
        )
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.item(id: "capture_to_3d")?.status, .waiting)
    try expectEqual(summary.item(id: "scene_load")?.status, .waiting)
    try expectFalse(summary.canClaimLocalShowcaseReady)
    try expectContains(summary.detail, "waiting")
}

private func testShowcaseEvidenceMarksReadyLocalDemo() throws {
    let session = showcaseEvidenceReadySession()
    let captureReceipt = CaptureGenerationReceiptBuilder.build(
        capture: guidedScanObjectCapture(),
        session: session,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let generationReceipt = GenerationResultReceiptBuilder.build(session: session)
    let sceneProof = ArtifactSceneLoadProof(
        status: .loaded,
        title: "SceneKit load proof: Loaded",
        detail: "SceneKit parsed the generated scene asset.",
        canOpenScene: true
    )
    let npcSummary = NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: npcTick(sessionId: session.sessionId, tickIndex: 3),
        tickHistoryCount: 3,
        isAdvancingTick: false,
        isRunningAutonomy: false,
        errorMessage: nil
    )
    let printReceipt = PrintFulfillmentReceiptBuilder.build(
        session: session,
        quote: localPrintQuote(),
        isLoading: false,
        errorMessage: nil,
        isApproved: true
    )

    let summary = ShowcaseEvidenceSummaryBuilder.build(
        captureReceipt: captureReceipt,
        generationReceipt: generationReceipt,
        sceneLoadProof: sceneProof,
        npcTickSummary: npcSummary,
        tickHistoryCount: 3,
        printFulfillmentReceipt: printReceipt
    )

    try expectEqual(summary.status, .ready)
    try expectTrue(summary.canClaimLocalShowcaseReady)
    try expectEqual(summary.item(id: "capture_to_3d")?.status, .ready)
    try expectEqual(summary.item(id: "generation_result")?.status, .ready)
    try expectEqual(summary.item(id: "scene_load")?.status, .ready)
    try expectEqual(summary.item(id: "npc_agent")?.status, .ready)
    try expectEqual(summary.item(id: "print_handoff")?.status, .ready)
    try expectContains(summary.title, "Showcase evidence ready")
}

private func testShowcaseEvidenceBlocksFailedSceneProof() throws {
    let session = showcaseEvidenceReadySession()
    let summary = ShowcaseEvidenceSummaryBuilder.build(
        captureReceipt: CaptureGenerationReceiptBuilder.build(
            capture: guidedScanObjectCapture(),
            session: session,
            captureGenerationReadiness: readyCaptureGenerationReadiness()
        ),
        generationReceipt: GenerationResultReceiptBuilder.build(session: session),
        sceneLoadProof: ArtifactSceneLoadProof(
            status: .failed,
            title: "SceneKit load proof: Failed",
            detail: "SceneKit could not parse the generated scene asset.",
            canOpenScene: false
        ),
        npcTickSummary: NPCAgentTickSummaryBuilder.build(
            session: session,
            latestTick: npcTick(sessionId: session.sessionId, tickIndex: 3),
            tickHistoryCount: 3,
            isAdvancingTick: false,
            isRunningAutonomy: false,
            errorMessage: nil
        ),
        tickHistoryCount: 3,
        printFulfillmentReceipt: PrintFulfillmentReceiptBuilder.build(
            session: session,
            quote: localPrintQuote(),
            isLoading: false,
            errorMessage: nil,
            isApproved: true
        )
    )

    try expectEqual(summary.status, .needsAttention)
    try expectEqual(summary.item(id: "scene_load")?.status, .needsAttention)
    try expectFalse(summary.canClaimLocalShowcaseReady)
    try expectContains(summary.item(id: "scene_load")?.detail ?? "", "could not parse")
}

private func testShowcaseEvidenceRedactsUnsafeDetails() throws {
    let unsafe = "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret"
    let summary = ShowcaseEvidenceSummaryBuilder.build(
        captureReceipt: CaptureGenerationReceipt(
            status: .ready,
            title: "Capture \(unsafe)",
            detail: "Capture detail \(unsafe)",
            rows: ["row \(unsafe)"],
            privacyNotes: ["privacy \(unsafe)"]
        ),
        generationReceipt: GenerationResultReceipt(
            status: .ready,
            title: "Generation \(unsafe)",
            detail: "Generation detail \(unsafe)",
            routeLabel: "multi_image \(unsafe)",
            rows: [
                GenerationResultReceiptRow(
                    id: "game_asset",
                    label: "Game asset",
                    status: .ready,
                    detail: "ready \(unsafe)"
                ),
            ],
            privacyNotes: ["generation privacy \(unsafe)"],
            canPresentResult: true
        ),
        sceneLoadProof: ArtifactSceneLoadProof(
            status: .loaded,
            title: "Loaded \(unsafe)",
            detail: "Scene detail \(unsafe)",
            canOpenScene: true
        ),
        npcTickSummary: NPCAgentTickSummary(
            status: .ready,
            title: "NPC \(unsafe)",
            detail: "NPC detail \(unsafe)",
            runtimeLabel: "runtime \(unsafe)",
            tickLabel: "tick 3",
            decisionLabel: "accepted",
            rows: ["npc row \(unsafe)"],
            privacyNotes: ["npc privacy \(unsafe)"]
        ),
        tickHistoryCount: 3,
        printFulfillmentReceipt: PrintFulfillmentReceipt(
            status: .ready,
            title: "Print \(unsafe)",
            detail: "Print detail \(unsafe)",
            rows: [
                PrintFulfillmentReceiptRow(
                    id: "provider",
                    label: "Provider",
                    status: .ready,
                    detail: "provider \(unsafe)"
                ),
            ],
            privacyNotes: ["print privacy \(unsafe)"],
            canApprove: false,
            canHandOffToProvider: true
        )
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key=secret")
}

private func testFinalShowcaseSummaryWaitsBeforeSession() throws {
    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: CaptureMediaSelection(mode: .singlePhoto),
        session: nil,
        npcTickHistoryCount: 0,
        printQuote: nil,
        providerReadiness: nil,
        providerReadinessError: nil
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.title, "Waiting for first myth session")
    try expectEqual(summary.stages.map(\.id), ["capture", "three_d", "npc_agent", "print", "resources"])
    try expectEqual(summary.stage(id: "capture")?.status, .waiting)
    try expectEqual(summary.stage(id: "three_d")?.status, .waiting)
    try expectEqual(summary.stage(id: "npc_agent")?.status, .waiting)
    try expectEqual(summary.stage(id: "print")?.status, .waiting)
    try expectEqual(summary.stage(id: "resources")?.status, .waiting)
}

private func testFinalShowcaseSummaryReadyForLocalDemo() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: nil,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.overallStatus, .readyForLocalDemo)
    try expectEqual(summary.title, session.mythSeed.title)
    try expectEqual(summary.stage(id: "capture")?.status, .ready)
    try expectEqual(summary.stage(id: "three_d")?.status, .ready)
    try expectContains(summary.stage(id: "three_d")?.detail ?? "", "local_stub")
    try expectContains(summary.stage(id: "three_d")?.detail ?? "", "multi_image")
    try expectEqual(summary.stage(id: "npc_agent")?.status, .ready)
    try expectContains(summary.stage(id: "npc_agent")?.detail ?? "", "3 saved ticks")
    try expectEqual(summary.stage(id: "print")?.status, .optional)
    try expectEqual(summary.stage(id: "resources")?.status, .ready)
    try expectEqual(summary.privacyNotes.count, 4)
}

private func testFinalShowcaseSummaryMarksPrintQuoteReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = PrintQuote(
        kind: "print_quote",
        provider: "local_stub",
        status: "draft_quote",
        sourceAssetUri: "local://generated-assets/myth_test.glb",
        printCandidateUri: "local://print-candidates/myth_test.3mf",
        currency: "USD",
        estimatedPriceCents: 1600,
        estimatedProductionDays: 5,
        estimatedShippingDays: 6,
        checkoutUrl: nil,
        requiresUserApproval: true,
        approvalReason: "review before fulfillment",
        quoteNotes: ["local quote stub"]
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 1,
        printQuote: quote,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(summary.overallStatus, .readyForLocalDemo)
    try expectEqual(summary.stage(id: "print")?.status, .ready)
    try expectContains(summary.stage(id: "print")?.detail ?? "", "USD 16.00")
}

private func testFinalShowcaseSummaryMarksProviderErrorNeedsAttention() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 1,
        printQuote: nil,
        providerReadiness: nil,
        providerReadinessError: "Backend preflight is not reachable yet."
    )

    try expectEqual(summary.overallStatus, .needsAttention)
    try expectEqual(summary.stage(id: "resources")?.status, .needsAttention)
    try expectContains(summary.stage(id: "resources")?.detail ?? "", "not reachable")
}

private func testFinalShowcaseSummaryRedactsUnsafeSourceText() throws {
    var session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    session.generatedAsset.prompt = "secret sk-test path /Users/me/key.jpg checkout https://checkout.example/pay"
    session.generatedAsset.uri = "file:///Users/me/private.glb"

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 1,
        printQuote: nil,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )
    let text = ([summary.title] + summary.stages.map(\.detail) + summary.privacyNotes).joined(separator: " ")

    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "checkout")
}

private func testFinalShowcaseSummaryIncludesBlockedFinalLaunchDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalAcceptanceStatus: "blocked",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(summary.overallStatus, .needsAttention)
    try expectEqual(summary.stage(id: "final_launch")?.status, .needsAttention)
    try expectContains(summary.stage(id: "final_launch")?.detail ?? "", "Final launch blocked")
}

private func testFinalShowcaseFinalLaunchStageUsesReceiptFirstBlocker() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            firstBlockerJSON: finalDemoLaunchTopLevelFirstBlockerJSON(),
            finalResourcesStatus: "blocked",
            finalAcceptanceStatus: "blocked",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let detail = summary.stage(id: "final_launch")?.detail ?? ""

    try expectEqual(summary.stage(id: "final_launch")?.status, .needsAttention)
    try expectContains(detail, "apply_final_resources")
    try expectContains(detail, "final_demo_launch_phase")
    try expectContains(detail, "make final-apply-resources")
}

private func testFinalShowcaseSummaryIncludesReadyFinalLaunchDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .ready,
        title: "Final launch ready",
        subtitle: "All final launch evidence is ready.",
        phaseRows: [],
        resourceFillGuideRows: ["Fill guide ready: required 2, optional 0, configured 2, secret 1."],
        applyPreviewRows: ["Apply preview ready: targets 2, missing 0, blocked 0, secret 4."],
        resourceHandoffRows: ["Resource handoff ready: ready 6, missing 0, blocked 0, manual 0."],
        resourceActions: [],
        acceptanceRows: ["Final acceptance ready."],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        liveProviderEvidenceRows: ["Live evidence ready: ready 5, missing 0, blocked 0, partial 0."],
        deployRunbookRows: ["iOS deploy runbook ready."],
        launchRehearsalRows: ["iOS launch rehearsal ready: ready 4, blocked 0, partial 0."],
        handoffRows: ["Final operator handoff ready."],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(summary.overallStatus, .readyForLocalDemo)
    try expectEqual(
        summary.stages.map(\.id),
        [
            "capture", "three_d", "npc_agent", "print", "resources",
            "provider_handoff", "local_smoke", "ios_deploy", "three_d_evaluation",
            "npc_evaluation", "operator_handoff", "final_launch",
        ]
    )
    try expectEqual(summary.stage(id: "provider_handoff")?.status, .ready)
    try expectEqual(summary.stage(id: "local_smoke")?.status, .ready)
    try expectEqual(summary.stage(id: "ios_deploy")?.status, .ready)
    try expectEqual(summary.stage(id: "three_d_evaluation")?.status, .ready)
    try expectEqual(summary.stage(id: "npc_evaluation")?.status, .ready)
    try expectEqual(summary.stage(id: "operator_handoff")?.status, .ready)
    try expectEqual(summary.stage(id: "final_launch")?.status, .ready)
}

private func testFinalShowcaseSummaryIncludesReadyProviderHandoffDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .ready,
        title: "Final launch ready",
        subtitle: "Provider handoff ready",
        phaseRows: [],
        resourceFillGuideRows: ["Fill guide ready: required 2, optional 0, configured 2, secret 1."],
        applyPreviewRows: ["Apply preview ready: targets 2, missing 0, blocked 0, secret 4."],
        resourceHandoffRows: ["Resource handoff ready: ready 6, missing 0, blocked 0, manual 0."],
        resourceActions: [],
        acceptanceRows: ["Final acceptance ready."],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        liveProviderEvidenceRows: ["Live evidence ready: ready 5, missing 0, blocked 0, partial 0."],
        deployRunbookRows: ["iOS deploy runbook ready."],
        launchRehearsalRows: ["iOS launch rehearsal ready: ready 4, blocked 0, partial 0."],
        handoffRows: ["Final operator handoff ready."],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let ids = summary.stages.map(\.id)
    let resourcesIndex = try require(ids.firstIndex(of: "resources"), "missing resources stage")
    let providerIndex = try require(ids.firstIndex(of: "provider_handoff"), "missing provider handoff stage")
    let localSmokeIndex = try require(ids.firstIndex(of: "local_smoke"), "missing local smoke stage")
    let stage = try require(summary.stage(id: "provider_handoff"), "missing provider handoff stage")

    try expectEqual(stage.label, "Provider Handoff")
    try expectEqual(stage.status, .ready)
    try expectContains(stage.detail, "Live evidence ready")
    try expectTrue(resourcesIndex < providerIndex)
    try expectTrue(providerIndex < localSmokeIndex)
}

private func testFinalShowcaseSummaryBlocksProviderHandoffDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalResourcesStatus: "missing",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            localShowcaseSmokeStatus: "succeeded",
            liveProviderEvidenceStatus: "missing",
            liveProviderEvidenceBlockerDetail: "Provider handoff requires configured evidence.",
            configuredEvidencePlanStatus: "blocked",
            printFulfillmentReadinessStatus: "partial",
            finalShowcaseReadinessStatus: "blocked",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "blocked",
            resourceHandoffBackendStatus: "missing",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "provide MESHY_API_KEY in final-resources.env"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let stage = try require(summary.stage(id: "provider_handoff"), "missing provider handoff stage")

    try expectEqual(summary.overallStatus, .needsAttention)
    try expectEqual(stage.status, .needsAttention)
    try expectContains(stage.detail, "Live evidence missing")
    try expectContains(stage.detail, "provide MESHY_API_KEY")
}

private func testFinalShowcaseSummaryBlocksProviderHandoffOnConfiguredEvidenceBundle() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "Configured bundle blocked",
        phaseRows: [],
        resourceFillGuideRows: ["Fill guide ready: required 2, optional 0, configured 2, secret 1."],
        applyPreviewRows: ["Apply preview ready: targets 2, missing 0, blocked 0, secret 4."],
        resourceHandoffRows: ["Resource handoff ready: ready 6, missing 0, blocked 0, manual 0."],
        resourceActions: [],
        acceptanceRows: ["Final acceptance ready."],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        liveProviderEvidenceRows: ["Live evidence ready: ready 5, missing 0, blocked 0, partial 0."],
        configuredEvidenceBundleRows: [
            "Configured bundle blocked: evidence ready 0, missing 5, blocked 0, partial 0; commands ready 3, blocked 2, consent 1.",
            "final_resource_fill_guide: blocked | make configured-live-evidence-bundle",
        ],
        deployRunbookRows: ["iOS deploy runbook ready."],
        launchRehearsalRows: ["iOS launch rehearsal ready: ready 4, blocked 0, partial 0."],
        handoffRows: ["Final operator handoff ready."],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let stage = try require(summary.stage(id: "provider_handoff"), "missing provider handoff stage")

    try expectEqual(summary.overallStatus, .needsAttention)
    try expectEqual(stage.status, .needsAttention)
    try expectContains(stage.detail, "Configured bundle blocked")
    try expectContains(stage.detail, "make configured-live-evidence-bundle")
}

private func testFinalShowcaseSummaryRedactsUnsafeConfiguredBundleProviderHandoff() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "Configured bundle blocked",
        phaseRows: [],
        resourceFillGuideRows: ["Fill guide ready: required 2, optional 0, configured 2, secret 1."],
        applyPreviewRows: ["Apply preview ready: targets 2, missing 0, blocked 0, secret 4."],
        resourceHandoffRows: ["Resource handoff ready: ready 6, missing 0, blocked 0, manual 0."],
        resourceActions: [],
        acceptanceRows: ["Final acceptance ready."],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        liveProviderEvidenceRows: ["Live evidence ready: ready 5, missing 0, blocked 0, partial 0."],
        configuredEvidenceBundleRows: [
            "Configured bundle blocked: sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
            "final_resource_fill_guide: blocked | make configured-live-evidence-bundle | sk-test /Users/zhexu/private",
        ],
        deployRunbookRows: ["iOS deploy runbook ready."],
        launchRehearsalRows: ["iOS launch rehearsal ready: ready 4, blocked 0, partial 0."],
        handoffRows: ["Final operator handoff ready."],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.stage(id: "provider_handoff")?.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalShowcaseSummaryRedactsUnsafeProviderHandoffDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "Provider handoff blocked",
        phaseRows: [],
        resourceFillGuideRows: [
            "Fill guide blocked: required 5, optional 5, configured 3, secret 4.",
            "MESHY_API_KEY: missing required secret | provide sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
        ],
        resourceActions: [],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        liveProviderEvidenceRows: [
            "Live evidence missing: ready 0, missing 5, blocked 0, partial 0. sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
            "provider_handoff: missing | make live-provider-evidence | sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
        ],
        deployRunbookRows: ["iOS deploy runbook ready."],
        launchRehearsalRows: ["iOS launch rehearsal ready: ready 4, blocked 0, partial 0."],
        handoffRows: ["Final operator handoff ready."],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.stage(id: "provider_handoff")?.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalShowcaseSummaryIncludesReadyLocalSmokeDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            localShowcaseSmokeStatus: "succeeded",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let ids = summary.stages.map(\.id)
    let localSmokeIndex = try require(ids.firstIndex(of: "local_smoke"), "missing local smoke stage")
    let threeDIndex = try require(ids.firstIndex(of: "three_d_evaluation"), "missing 3D evaluation stage")
    let localSmoke = try require(summary.stage(id: "local_smoke"), "missing local smoke stage")

    try expectEqual(localSmoke.label, "Local Smoke")
    try expectEqual(localSmoke.status, .ready)
    try expectContains(localSmoke.detail, "Local showcase smoke ready")
    try expectContains(localSmoke.detail, "HTTP 6")
    try expectContains(localSmoke.detail, "NPC ticks 2")
    try expectContains(localSmoke.detail, "downloads 3")
    try expectTrue(localSmokeIndex < threeDIndex)
}

private func testFinalShowcaseSummaryBlocksFailedLocalSmokeDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "Local smoke failed",
        phaseRows: [],
        resourceActions: [],
        acceptanceRows: [],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: [
            "Local showcase smoke failed: failed 1, HTTP 1.",
            "upload_guided_scan_capture: failed | Authorization=Bearer sk-local data:image/png;base64,AAAA /Users/zhexu/private checkout_url",
        ],
        handoffRows: [],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let stage = try require(summary.stage(id: "local_smoke"), "missing local smoke stage")
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(stage.status, .needsAttention)
    try expectContains(stage.detail, "[withheld]")
    try expectNotContains(text, "sk-local")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "data:image")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalShowcaseSummaryIncludesReadyIOSDeployDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            localShowcaseSmokeStatus: "succeeded",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let ids = summary.stages.map(\.id)
    let localSmokeIndex = try require(ids.firstIndex(of: "local_smoke"), "missing local smoke stage")
    let deployIndex = try require(ids.firstIndex(of: "ios_deploy"), "missing iOS deploy stage")
    let threeDIndex = try require(ids.firstIndex(of: "three_d_evaluation"), "missing 3D evaluation stage")
    let stage = try require(summary.stage(id: "ios_deploy"), "missing iOS deploy stage")

    try expectEqual(stage.label, "iOS Deploy")
    try expectEqual(stage.status, .ready)
    try expectContains(stage.detail, "iOS launch rehearsal ready")
    try expectContains(stage.detail, "ready 4")
    try expectTrue(localSmokeIndex < deployIndex)
    try expectTrue(deployIndex < threeDIndex)
}

private func testFinalShowcaseSummaryBlocksIOSDeployDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            localShowcaseSmokeStatus: "succeeded",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "blocked",
            iosDeployRunbookSlotStatus: "blocked",
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalAction: "make ios-device-launch-rehearsal",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let stage = try require(summary.stage(id: "ios_deploy"), "missing iOS deploy stage")

    try expectEqual(summary.overallStatus, .needsAttention)
    try expectEqual(stage.status, .needsAttention)
    try expectContains(stage.detail, "iOS launch rehearsal blocked")
    try expectContains(stage.detail, "make final-handoff-index")
}

private func testFinalShowcaseSummaryRedactsUnsafeIOSDeployDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "iOS deploy blocked",
        phaseRows: [],
        resourceActions: [],
        acceptanceRows: [],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        localShowcaseSmokeRows: ["Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3."],
        deployRunbookRows: [
            "iOS deploy runbook blocked.",
            "backend_base_url: blocked required | sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
        ],
        launchRehearsalRows: [
            "iOS launch rehearsal blocked: ready 3, blocked 1, partial 0.",
            "final_handoff_index: blocked | make final-handoff-index | sk-test /Users/zhexu/private file:///tmp/private checkout_url Bearer token",
        ],
        handoffRows: [],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.stage(id: "ios_deploy")?.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalShowcaseSummaryIncludesReadyThreeDEvaluationDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let ids = summary.stages.map(\.id)
    let threeDIndex = try require(ids.firstIndex(of: "three_d_evaluation"), "missing 3D evaluation stage")
    let npcIndex = try require(ids.firstIndex(of: "npc_evaluation"), "missing NPC evaluation stage")

    try expectEqual(summary.overallStatus, .readyForLocalDemo)
    try expectEqual(summary.stage(id: "three_d_evaluation")?.status, .ready)
    try expectContains(summary.stage(id: "three_d_evaluation")?.detail ?? "", "20 cases")
    try expectTrue(threeDIndex < npcIndex)
}

private func testFinalShowcaseSummaryWaitsForMissingThreeDEvaluationDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "missing",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.stage(id: "three_d_evaluation")?.status, .waiting)
    try expectContains(summary.stage(id: "three_d_evaluation")?.detail ?? "", "Run local 3D evaluation")
}

private func testFinalShowcaseSummaryWaitsForMissingNPCEvaluationDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidencePlanStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            printFulfillmentReadinessStatus: "ready",
            finalResourceApplyPreviewStatus: "ready",
            npcEvaluationStatus: "missing",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        error: nil
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.stage(id: "npc_evaluation")?.status, .waiting)
    try expectContains(summary.stage(id: "npc_evaluation")?.detail ?? "", "Run local NPC Agent evaluation")
}

private func testFinalShowcaseSummaryRedactsUnsafeThreeDEvaluationDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "3D evaluation blocked",
        phaseRows: [],
        resourceActions: [],
        acceptanceRows: [],
        threeDEvaluationRows: [
            "failed Authorization=Bearer test-secret private_message: raw /Users/zhexu/private file:///tmp/private"
        ],
        npcEvaluationRows: ["NPC Agent evaluation ready: 6 cases passed."],
        handoffRows: [],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let detail = summary.stage(id: "three_d_evaluation")?.detail ?? ""

    try expectEqual(summary.stage(id: "three_d_evaluation")?.status, .needsAttention)
    try expectContains(detail, "[withheld]")
    try expectNotContains(detail, "test-secret")
    try expectNotContains(detail, "private_message:")
    try expectNotContains(detail, "/Users/")
    try expectNotContains(detail, "file:///")
}

private func testFinalShowcaseSummaryRedactsUnsafeFinalLaunchDigest() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token private_message: raw",
        phaseRows: [],
        resourceActions: [],
        acceptanceRows: [],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        npcEvaluationRows: ["failed Authorization=Bearer test-secret private_message: raw"],
        handoffRows: ["checkout_url=https://pay.example /Users/zhexu/private"],
        commandRows: [],
        notes: []
    )

    let summary = FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let text = ([summary.title] + summary.stages.map(\.detail) + summary.privacyNotes).joined(separator: " ")

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "private_message:")
}

private func testContextCapsuleReviewWaitsForMissingSummary() throws {
    let review = ContextCapsuleReviewBuilder.build(
        currentTheme: "",
        desiredTone: "tender, strange",
        isApproved: false
    )

    try expectEqual(review.status, .waiting)
    try expectContains(review.title, "incomplete")
    try expectContains(review.detail, "theme")
    try expectEqual(review.canApprove, false)
    try expectEqual(review.canForge, false)
}

private func testContextCapsuleReviewWaitsForApproval() throws {
    let review = ContextCapsuleReviewBuilder.build(
        currentTheme: "deadline pressure",
        desiredTone: "tender, strange",
        isApproved: false
    )

    try expectEqual(review.status, .waiting)
    try expectContains(review.title, "Review context capsule")
    try expectContains(review.detail, "Approve")
    try expectEqual(review.canApprove, true)
    try expectEqual(review.canForge, false)
    try expectContains(review.summaryLines.joined(separator: " "), "deadline pressure")
}

private func testContextCapsuleReviewMarksApprovedSummaryReady() throws {
    let review = ContextCapsuleReviewBuilder.build(
        currentTheme: "deadline pressure",
        desiredTone: "tender, strange",
        isApproved: true
    )

    try expectEqual(review.status, .ready)
    try expectContains(review.title, "Context capsule approved")
    try expectEqual(review.canApprove, true)
    try expectEqual(review.canForge, true)
    try expectContains(review.summaryLines.joined(separator: " "), "deadline pressure")
    try expectContains(review.summaryLines.joined(separator: " "), "tender, strange")
    try expectContains(review.privacyNotes.joined(separator: " "), "No raw")
}

private func testContextCapsuleReviewRedactsUnsafeText() throws {
    let review = ContextCapsuleReviewBuilder.build(
        currentTheme: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap",
        desiredTone: "checkout_url Bearer token",
        isApproved: true
    )
    let text = String(decoding: try PMFJSON.encoder.encode(review), as: UTF8.self)

    try expectEqual(review.status, .ready)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testForgeReadinessWaitsForCapture() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: CaptureGenerationReadinessBuilder.build(
            selection: CaptureMediaSelection(mode: .guidedScan),
            providerReadiness: localDemoProviderReadiness(),
            providerReadinessError: nil
        ),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.canForge, false)
    try expectEqual(summary.routeLabel, "waiting")
    try expectContains(summary.title, "Forge waiting")
    try expectContains(summary.rows.joined(separator: " "), "Capture")
}

private func testForgeReadinessWaitsForContextApproval() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(),
        contextCapsuleReview: ContextCapsuleReviewBuilder.build(
            currentTheme: "deadline pressure",
            desiredTone: "tender, strange",
            isApproved: false
        ),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.canForge, false)
    try expectEqual(summary.routeLabel, "waiting")
    try expectContains(summary.rows.joined(separator: " "), "Context")
    try expectContains(summary.detail, "Approve")
}

private func testForgeReadinessMarksLocalDemoReady() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.canForge, true)
    try expectEqual(summary.routeLabel, "local_demo")
    try expectContains(summary.title, "Forge ready")
    try expectContains(summary.rows.joined(separator: " "), "3D")
    try expectContains(summary.rows.joined(separator: " "), "NPC Agent")
    try expectContains(summary.privacyNotes.joined(separator: " "), "backend-only")
}

private func testForgeReadinessMarksProviderErrorNeedsAttention() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: nil,
        providerReadinessError: "Backend preflight is not reachable yet.",
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )

    try expectEqual(summary.status, .needsAttention)
    try expectEqual(summary.canForge, false)
    try expectEqual(summary.routeLabel, "needs_attention")
    try expectContains(summary.detail, "not reachable")
}

private func testForgeReadinessMarksMissingConfiguredProviders() throws {
    let readiness = ProviderReadinessResponse(
        overallDemoReady: false,
        overallRealReady: false,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "meshy",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["MESHY_API_KEY"]
            ),
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "openai",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["OPENAI_API_KEY"]
            ),
        ]
    )

    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(providerReadiness: readiness),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: readiness,
        providerReadinessError: nil,
        npcAgentModeSummary: missingOpenAINPCAgentModeSummary()
    )

    try expectEqual(summary.status, .needsAttention)
    try expectEqual(summary.canForge, false)
    try expectEqual(summary.routeLabel, "needs_attention")
    try expectContains(summary.detail, "MESHY_API_KEY")
    try expectContains(summary.detail, "OPENAI_API_KEY")
}

private func testForgeReadinessRedactsUnsafeText() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: ProviderReadinessResponse(
            overallDemoReady: false,
            overallRealReady: false,
            providers: [
                ProviderReadinessItem(
                    kind: "three_d",
                    selectedProvider: "meshy sk-test",
                    status: "Authorization Bearer token /Users/zhexu",
                    isDemoReady: false,
                    isRealProviderReady: false,
                    missingEnv: ["MESHY_API_KEY", "sk-test"]
                ),
            ]
        ),
        providerReadinessError: "Authorization Bearer token sk-test /Users/zhexu file:///tmp/private local-capture://cap checkout_url",
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
}

private func testForgeActionGateDisablesWithoutCapture() throws {
    let gate = ForgeActionGateBuilder.build(
        isMediaReadyForUpload: false,
        contextCapsuleReview: approvedContextCapsuleReview(),
        forgeReadinessSummary: readyForgeReadinessSummary()
    )

    try expectEqual(gate.isEnabled, false)
    try expectEqual(gate.title, "Forge Myth")
    try expectEqual(gate.disabledReason, "capture_required")
    try expectContains(gate.detail, "Capture")
}

private func testForgeActionGateDisablesUntilContextApproved() throws {
    let gate = ForgeActionGateBuilder.build(
        isMediaReadyForUpload: true,
        contextCapsuleReview: ContextCapsuleReviewBuilder.build(
            currentTheme: "lost compass",
            desiredTone: "quiet",
            isApproved: false
        ),
        forgeReadinessSummary: readyForgeReadinessSummary()
    )

    try expectEqual(gate.isEnabled, false)
    try expectEqual(gate.disabledReason, "context_approval_required")
    try expectContains(gate.detail, "Approve")
}

private func testForgeActionGateDisablesWhenReadinessNeedsAttention() throws {
    let summary = ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(providerReadiness: missingProviderReadiness()),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: missingProviderReadiness(),
        providerReadinessError: nil,
        npcAgentModeSummary: missingOpenAINPCAgentModeSummary()
    )
    let gate = ForgeActionGateBuilder.build(
        isMediaReadyForUpload: true,
        contextCapsuleReview: approvedContextCapsuleReview(),
        forgeReadinessSummary: summary
    )

    try expectEqual(gate.isEnabled, false)
    try expectEqual(gate.disabledReason, "forge_readiness_required")
    try expectContains(gate.detail, "MESHY_API_KEY")
}

private func testForgeActionGateEnablesLocalDemoForge() throws {
    let gate = ForgeActionGateBuilder.build(
        isMediaReadyForUpload: true,
        contextCapsuleReview: approvedContextCapsuleReview(),
        forgeReadinessSummary: readyForgeReadinessSummary()
    )

    try expectEqual(gate.isEnabled, true)
    try expectEqual(gate.disabledReason, nil)
    try expectContains(gate.detail, "local_demo")
}

private func testForgeActionGateRedactsUnsafeDetail() throws {
    let summary = ForgeReadinessSummary(
        status: .needsAttention,
        title: "Forge needs attention",
        detail: "Authorization Bearer token sk-test /Users/zhexu file:///tmp/private local-capture://cap checkout_url",
        routeLabel: "needs_attention",
        rows: [],
        privacyNotes: [],
        canForge: false
    )
    let gate = ForgeActionGateBuilder.build(
        isMediaReadyForUpload: true,
        contextCapsuleReview: approvedContextCapsuleReview(),
        forgeReadinessSummary: summary
    )
    let text = String(decoding: try PMFJSON.encoder.encode(gate), as: UTF8.self)

    try expectEqual(gate.isEnabled, false)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
}

private func testDevicePreflightBlocksLoopbackBackendURL() throws {
    let summary = devicePreflightSummary(backendBaseURL: URL(string: "http://127.0.0.1:8080")!)

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "backend_url")?.status, .blocked)
    try expectContains(summary.item(id: "backend_url")?.detail ?? "", "iPhone")
    try expectContains(summary.backendBaseURL, "127.0.0.1")
}

private func testDevicePreflightWaitsForUncheckedBackendHealth() throws {
    let summary = devicePreflightSummary(backendBaseURL: URL(string: "http://192.168.1.10:8080")!)

    try expectEqual(summary.item(id: "backend_url")?.status, .waiting)
    try expectContains(summary.item(id: "backend_url")?.detail ?? "", "Check Backend")
}

private func testDevicePreflightMarksBackendHealthChecking() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        backendHealthProbe: BackendHealthProbe(status: .checking, detail: "Checking backend health.")
    )

    try expectEqual(summary.item(id: "backend_url")?.status, .waiting)
    try expectContains(summary.item(id: "backend_url")?.detail ?? "", "Checking")
}

private func testDevicePreflightMarksReachableBackendHealthReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        backendHealthProbe: BackendHealthProbe(status: .reachable, detail: "Backend /health returned ok."),
        providerReadiness: localDemoProviderReadiness(),
        finalShowcaseSummary: finalShowcaseSummary(session: session, npcTickHistoryCount: 3)
    )

    try expectEqual(summary.item(id: "backend_url")?.status, .ready)
    try expectEqual(summary.overallStatus, .ready)
}

private func testDevicePreflightBlocksUnreachableBackendHealthAndRedacts() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        backendHealthProbe: BackendHealthProbe(
            status: .unreachable,
            detail: "Authorization=Bearer token sk-test /Users/zhexu/file local-capture://x checkout_url"
        )
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "backend_url")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout_url")
}

private func testDevicePreflightBlocksNonOKBackendHealth() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        backendHealthProbe: BackendHealthProbe(response: BackendHealthResponse(status: "degraded"))
    )

    try expectEqual(summary.item(id: "backend_url")?.status, .blocked)
    try expectContains(summary.item(id: "backend_url")?.detail ?? "", "degraded")
}

private func testDevicePreflightKeepsLoopbackBlockedWithReachableHealth() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://127.0.0.1:8080")!,
        backendHealthProbe: BackendHealthProbe(status: .reachable, detail: "Backend /health returned ok.")
    )

    try expectEqual(summary.item(id: "backend_url")?.status, .blocked)
    try expectContains(summary.item(id: "backend_url")?.detail ?? "", "iPhone")
}

private func testDevicePreflightWaitsForProviderReadiness() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        providerReadiness: nil
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.item(id: "providers")?.status, .waiting)
    try expectContains(summary.item(id: "providers")?.detail ?? "", "readiness")
}

private func testDevicePreflightBlocksAndRedactsProviderError() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        providerReadiness: nil,
        providerReadinessError: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "providers")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDevicePreflightWaitsForFinalLaunchReport() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: nil,
        finalDemoLaunchError: nil
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.item(id: "final_launch")?.status, .waiting)
    try expectContains(summary.item(id: "final_launch")?.detail ?? "", "launch")
}

private func testDevicePreflightUsesFinalLaunchFirstBlockerDetail() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        firstBlockerJSON: finalDemoLaunchTopLevelFirstBlockerJSON(),
        finalResourcesStatus: "blocked"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        backendHealthProbe: BackendHealthProbe(status: .reachable, detail: "Backend /health returned ok."),
        finalDemoLaunch: report
    )
    let detail = summary.item(id: "final_launch")?.detail ?? ""

    try expectEqual(summary.item(id: "final_launch")?.status, .blocked)
    try expectContains(detail, "apply_final_resources")
    try expectContains(detail, "final_demo_launch_phase")
    try expectContains(detail, "make final-apply-resources")
}

private func testDevicePreflightMapsFinalLaunchPartialToWaiting() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(overallStatus: "partial")
    )

    try expectEqual(summary.item(id: "final_launch")?.status, .waiting)
    try expectContains(summary.item(id: "final_launch")?.detail ?? "", "partial")
}

private func testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "partial",
            finalResourcesStatus: "missing",
            finalResourcesAction: "run make final-resource-init"
        )
    )

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_resources")?.status, .waiting)
    try expectContains(summary.item(id: "final_resources")?.detail ?? "", "missing")
    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .blocked)
}

private func testDevicePreflightMarksReadyFinalResourcesPreflight() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready"
        )
    )

    try expectEqual(summary.item(id: "final_resources")?.status, .ready)
    try expectContains(summary.item(id: "final_resources")?.detail ?? "", "ready")
}

private func testDevicePreflightBlocksAndRedactsFinalResourcesPreflight() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "partial",
            finalResourcesStatus: "blocked",
            finalResourcesAction: "remove sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
        )
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_resources")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDevicePreflightWaitsForMissingFinalResourceRequirements() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.finalResourceRequirements = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_resource_requirements")?.status, .waiting)
    try expectContains(summary.item(id: "final_resource_requirements")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnFinalResourceRequirementsFirstBlocker() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport()
    )
    let detail = summary.item(id: "final_resource_requirements")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_resource_requirements")?.status, .blocked)
    try expectContains(detail, "missing 5")
    try expectContains(detail, "First blocker: MESHY_API_KEY missing")
    try expectContains(detail, "provide MESHY_API_KEY in final-resources.env")
    try expectContains(detail, "Backend-only secret for live Meshy 3D generation.")
    try expectContains(detail, "backend_provider")
    try expectContains(detail, "services/backend/.local/final-resources.env")
    try expectContains(detail, "make final-resources-preflight")
    try expectContains(detail, "Action: provide MESHY_API_KEY in final-resources.env")
}

private func testDevicePreflightMarksReadyFinalResourceRequirements() throws {
    var report = finalDemoLaunchReport(overallStatus: "ready")
    report.finalResourceRequirements = readyFinalResourceRequirementsReport()
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let detail = summary.item(id: "final_resource_requirements")?.detail ?? ""

    try expectEqual(summary.item(id: "final_resource_requirements")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "total 13")
    try expectContains(detail, "ready 13")
    try expectContains(detail, "missing 0")
    try expectContains(detail, "required 5")
    try expectContains(detail, "secret 4")
}

private func testDevicePreflightRedactsUnsafeFinalResourceRequirementsFirstBlockerDetail() throws {
    var report = finalDemoLaunchReport()
    report.finalResourceRequirements = blockedFinalResourceRequirementsReport(
        firstBlocker: FinalResourceRequirementsFirstBlocker(
            id: "MESHY_API_KEY",
            label: "Meshy API key",
            status: "missing",
            classification: "missing_required_value",
            command: "paste sk-test from /Users/zhexu/private file:///tmp local-capture://cap checkout_url Bearer token",
            detail: "Authorization Bearer token api_key=secret checkout_url /Users/zhexu/private",
            domain: "backend_provider",
            destination: "services/backend/.local/final-resources.env",
            validationCommand: "make final-resources-preflight"
        )
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_resource_requirements")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingFinalResourceFillGuide() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.finalResourceFillGuide = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .waiting)
    try expectContains(summary.item(id: "final_resource_fill_guide")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnRequiredFinalResourceFillGuideInputs() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport()
    )

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .blocked)
    try expectContains(summary.item(id: "final_resource_fill_guide")?.detail ?? "", "required 5")
    try expectContains(
        summary.item(id: "final_resource_fill_guide")?.detail ?? "",
        "First blocker: MESHY_API_KEY missing"
    )
    try expectContains(summary.item(id: "final_resource_fill_guide")?.detail ?? "", "MESHY_API_KEY")
    try expectContains(
        summary.item(id: "final_resource_fill_guide")?.detail ?? "",
        "Backend-only secret for live Meshy 3D generation."
    )
    try expectContains(
        summary.item(id: "final_resource_fill_guide")?.detail ?? "",
        "make final-resources-preflight"
    )
    try expectContains(
        summary.item(id: "final_resource_fill_guide")?.detail ?? "",
        "make final-resource-requirements"
    )
}

private func testDevicePreflightMarksReadyFinalResourceFillGuide() throws {
    var report = finalDemoLaunchReport(overallStatus: "ready")
    report.finalResourceFillGuide = readyFinalResourceFillGuideReport()
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .ready)
    try expectContains(summary.item(id: "final_resource_fill_guide")?.detail ?? "", "configured 2")
}

private func testDevicePreflightRedactsUnsafeFinalResourceFillGuideDetail() throws {
    var report = finalDemoLaunchReport()
    report.finalResourceFillGuide = blockedFinalResourceFillGuideReport(
        fillAction: "paste sk-test from /Users/zhexu/private file:///tmp local-capture://cap checkout_url Bearer token"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDevicePreflightRedactsUnsafeFinalResourceFillGuideFirstBlockerDetail() throws {
    var report = finalDemoLaunchReport()
    report.finalResourceFillGuide = blockedFinalResourceFillGuideReport(
        firstBlocker: FinalResourceFillGuideFirstBlocker(
            id: "MESHY_API_KEY",
            label: "Meshy API key",
            status: "missing",
            classification: "missing_required_value",
            command: "paste sk-test from /Users/zhexu/private file:///tmp local-capture://cap checkout_url Bearer token",
            detail: "Authorization Bearer token api_key=secret checkout_url /Users/zhexu/private",
            domain: "backend_provider",
            inputSource: "services/backend/.local/final-resources.env",
            writeDestination: "services/backend/.env",
            validationCommand: "make final-resources-preflight"
        )
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_resource_fill_guide")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingFinalResourceApplyPreview() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.finalResourceApplyPreview = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_resource_apply_preview")?.status, .waiting)
    try expectContains(summary.item(id: "final_resource_apply_preview")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnFinalResourceApplyPreviewFirstBlocker() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport()
    )
    let detail = summary.item(id: "final_resource_apply_preview")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_resource_apply_preview")?.status, .blocked)
    try expectContains(detail, "missing 5")
    try expectContains(detail, "First blocker: backend_env missing")
    try expectContains(detail, "make final-apply-resources")
    try expectContains(detail, "blocked by MESHY_API_KEY")
    try expectContains(detail, "services/backend/.env")
    try expectContains(detail, "services/backend/scripts/write_backend_env.sh")
    try expectContains(detail, "blocked_by MESHY_API_KEY")
    try expectContains(detail, "make final-resources-preflight")
    try expectContains(detail, "Command: make final-resource-apply-preview")
}

private func testDevicePreflightMarksReadyFinalResourceApplyPreview() throws {
    var report = finalDemoLaunchReport(overallStatus: "ready")
    report.finalResourceApplyPreview = readyFinalResourceApplyPreviewReport()
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let detail = summary.item(id: "final_resource_apply_preview")?.detail ?? ""

    try expectEqual(summary.item(id: "final_resource_apply_preview")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "ready 8")
    try expectContains(detail, "missing 0")
    try expectContains(detail, "targets 2")
}

private func testDevicePreflightRedactsUnsafeFinalResourceApplyPreviewFirstBlockerDetail() throws {
    var report = finalDemoLaunchReport()
    report.finalResourceApplyPreview = blockedFinalResourceApplyPreviewReport(
        firstBlocker: FinalResourceApplyPreviewFirstBlocker(
            id: "backend_env",
            label: "Backend env",
            status: "blocked",
            classification: "missing_required_value",
            command: "paste sk-test from /Users/zhexu/private file:///tmp local-capture://cap checkout_url Bearer token",
            detail: "Authorization Bearer token api_key=secret checkout_url /Users/zhexu/private",
            destination: "services/backend/.env",
            writer: "services/backend/scripts/write_backend_env.sh",
            blockedBy: ["MESHY_API_KEY", "OPENAI_API_KEY"],
            validationCommand: "make final-resources-preflight"
        )
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_resource_apply_preview")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingIOSDeployRunbook() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.iosDeployRunbook = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "ios_deploy_runbook")?.status, .waiting)
    try expectContains(summary.item(id: "ios_deploy_runbook")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnIOSDeployRunbookCommandStep() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeployRunbookStatus: "blocked",
            iosDeployRunbookSlotStatus: "blocked",
            iosDeployRunbookAction: "provide DEVELOPMENT_TEAM and rerun mobile deploy preflight",
            iosDeployRunbookCommand: "make mobile-deploy-preflight"
        )
    )
    let detail = summary.item(id: "ios_deploy_runbook")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "ios_deploy_runbook")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "mobile_xcode_build")
    try expectContains(detail, "Xcode build")
    try expectContains(detail, "make mobile-xcode-build")
    try expectContains(detail, "requires local Xcode")
    try expectContains(detail, "provide DEVELOPMENT_TEAM")
}

private func testDevicePreflightMarksReadyIOSDeployRunbook() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeployRunbookStatus: "ready",
            iosDeployRunbookSlotStatus: "ready",
            iosDeployRunbookThreeDSlotStatus: "ready"
        )
    )
    let detail = summary.item(id: "ios_deploy_runbook")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_deploy_runbook")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "mode local")
    try expectContains(detail, "required slots 3")
    try expectContains(detail, "commands 2")
    try expectContains(detail, "commands_run=false")
    try expectContains(detail, "global_mutation=false")
}

private func testDevicePreflightRedactsUnsafeIOSDeployRunbookDetail() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        iosDeployRunbookStatus: "blocked",
        iosDeployRunbookSlotStatus: "blocked",
        iosDeployRunbookAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret",
        iosDeployRunbookCommand: "make mobile-deploy-preflight sk-test /Users/zhexu/private file:///tmp/private"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "ios_deploy_runbook")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingIOSDeviceEvidenceBundle() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.iosDeviceEvidenceBundle = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "ios_device_evidence_bundle")?.status, .waiting)
    try expectContains(summary.item(id: "ios_device_evidence_bundle")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnIOSDeviceEvidenceSlot() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceEvidenceStatus: "blocked",
            iosDeviceEvidenceSlotStatus: "blocked",
            iosDeviceEvidenceAction: "run make mobile-deploy-preflight after backend is running",
            iosDeviceEvidenceDetail: "Run mobile deploy preflight after backend-device-demo is reachable.",
            iosDeviceEvidenceCommand: "make mobile-deploy-preflight"
        )
    )
    let detail = summary.item(id: "ios_device_evidence_bundle")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "ios_device_evidence_bundle")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "backend_device_server")
    try expectContains(detail, "make backend-device-demo")
    try expectContains(detail, "backend_health_not_proven")
    try expectContains(detail, "Run mobile deploy preflight")
    try expectContains(detail, "Action: run make mobile-deploy-preflight")
}

private func testDevicePreflightMarksReadyIOSDeviceEvidenceBundle() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceEvidenceStatus: "ready",
            iosDeviceEvidenceSlotStatus: "ready"
        )
    )
    let detail = summary.item(id: "ios_device_evidence_bundle")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_device_evidence_bundle")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "ready 4")
    try expectContains(detail, "blocked 0")
    try expectContains(detail, "required 4")
    try expectContains(detail, "global 1")
    try expectContains(detail, "commands_run=false")
    try expectContains(detail, "xcode=false")
}

private func testDevicePreflightRedactsUnsafeIOSDeviceEvidenceBundleDetail() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        iosDeviceEvidenceStatus: "blocked",
        iosDeviceEvidenceSlotStatus: "blocked",
        iosDeviceEvidenceAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret",
        iosDeviceEvidenceDetail: "Authorization Bearer token api_key=secret checkout_url /Users/zhexu/private",
        iosDeviceEvidenceCommand: "make mobile-deploy-preflight sk-test /Users/zhexu/private file:///tmp/private"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "ios_device_evidence_bundle")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingIOSLaunchRehearsalReadiness() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.iosDeviceLaunchRehearsalReadiness = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "ios_device_launch_rehearsal_readiness")?.status, .waiting)
    try expectContains(summary.item(id: "ios_device_launch_rehearsal_readiness")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnIOSLaunchRehearsalReadiness() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalAction: "rerun make ios-device-launch-rehearsal",
            iosDeviceLaunchRehearsalCommand: "make final-handoff-index"
        )
    )
    let detail = summary.item(id: "ios_device_launch_rehearsal_readiness")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "ios_device_launch_rehearsal_readiness")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "ready 3")
    try expectContains(detail, "blocked 1")
    try expectContains(detail, "final_handoff_index")
    try expectContains(detail, "make final-handoff-index")
    try expectContains(detail, "saved_report")
    try expectContains(detail, "rerun make ios-device-launch-rehearsal")
    try expectContains(detail, "commands_run=false")
}

private func testDevicePreflightMarksReadyIOSLaunchRehearsalReadiness() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceLaunchRehearsalStatus: "ready"
        )
    )
    let detail = summary.item(id: "ios_device_launch_rehearsal_readiness")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_device_launch_rehearsal_readiness")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "ready 4")
    try expectContains(detail, "blocked 0")
    try expectContains(detail, "fresh_report")
    try expectContains(detail, "services/backend/.local/ios-device-launch-rehearsal.json")
    try expectContains(detail, "commands_run=false")
    try expectContains(detail, "xcode=false")
}

private func testDevicePreflightShowsStaleIOSLaunchRehearsalFreshness() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "blocked",
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalAction: "rerun make ios-device-launch-rehearsal",
            iosDeviceLaunchRehearsalFreshnessStatus: "stale",
            iosDeviceLaunchRehearsalFreshnessClassification: "stale_report",
            iosDeviceLaunchSourceFreshnessStatus: "stale",
            iosDeviceLaunchSourceFreshnessClassification: "stale_source",
            iosDeviceLaunchSourceFreshnessSummaryJSON: #"{"fresh": 3, "stale": 1, "unknown": 0}"#
        )
    )
    let detail = summary.item(id: "ios_device_launch_rehearsal_readiness")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_device_launch_rehearsal_readiness")?.status, .blocked)
    try expectContains(detail, "Freshness: stale_report")
    try expectContains(detail, "Source freshness: 3 fresh, 1 stale, 0 unknown")
    try expectContains(detail, "stale_source")
}

private func testDevicePreflightRedactsUnsafeIOSLaunchRehearsalReadiness() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        iosDeviceLaunchRehearsalStatus: "blocked",
        iosDeviceLaunchRehearsalAction: "rerun sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret",
        iosDeviceLaunchRehearsalCommand: "make ios-device-launch-rehearsal sk-test /Users/zhexu/private file:///tmp/private",
        iosDeviceLaunchRehearsalFreshnessClassification: "stale_report sk-test /Users/zhexu/private file:///tmp/private"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "ios_device_launch_rehearsal_readiness")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingIOSDeviceLaunchCertificate() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.iosDeviceLaunchCertificate = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "ios_device_launch_certificate")?.status, .waiting)
    try expectContains(summary.item(id: "ios_device_launch_certificate")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnIOSDeviceLaunchCertificateGate() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceLaunchCertificateStatus: "blocked",
            iosDeviceLaunchCertificateGateStatus: "blocked",
            iosDeviceLaunchCertificateAction: "provide iOS deploy config and rerun mobile deploy preflight"
        )
    )
    let detail = summary.item(id: "ios_device_launch_certificate")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "ios_device_launch_certificate")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "ready 4")
    try expectContains(detail, "blocked 1")
    try expectContains(detail, "provide iOS deploy config")
    try expectContains(detail, "final_handoff_index")
    try expectContains(detail, "make final-handoff-index")
    try expectContains(detail, "commands_run=false")
}

private func testDevicePreflightMarksReadyIOSDeviceLaunchCertificate() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            iosDeviceLaunchCertificateStatus: "ready",
            iosDeviceLaunchCertificateGateStatus: "ready"
        )
    )
    let detail = summary.item(id: "ios_device_launch_certificate")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_device_launch_certificate")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "mode local")
    try expectContains(detail, "ready 8")
    try expectContains(detail, "blocked 0")
    try expectContains(detail, "writes_ios_config=false")
    try expectContains(detail, "xcode=false")
}

private func testDevicePreflightShowsIOSDeviceLaunchCertificateConsentGate() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "blocked",
            iosDeviceLaunchCertificateStatus: "blocked",
            iosDeviceLaunchCertificateGateStatus: "ready",
            iosDeviceLaunchCertificateAction: "run configured final acceptance with live provider consent"
        )
    )
    let detail = summary.item(id: "ios_device_launch_certificate")?.detail ?? ""

    try expectEqual(summary.item(id: "ios_device_launch_certificate")?.status, .blocked)
    try expectContains(detail, "configured_final_acceptance")
    try expectContains(detail, "requires consent")
    try expectContains(detail, "final-acceptance-configured")
}

private func testDevicePreflightRedactsUnsafeIOSDeviceLaunchCertificate() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        iosDeviceLaunchCertificateStatus: "blocked",
        iosDeviceLaunchCertificateGateStatus: "blocked",
        iosDeviceLaunchCertificateAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "ios_device_launch_certificate")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightWaitsForMissingFinalClosurePacket() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.finalLaunchClosurePacket = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_launch_closure_packet")?.status, .waiting)
    try expectContains(summary.item(id: "final_launch_closure_packet")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnFinalClosurePacketFirstBlocker() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(overallStatus: "ready")
    )
    let detail = summary.item(id: "final_launch_closure_packet")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_launch_closure_packet")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "sections 6")
    try expectContains(detail, "blocked 4")
    try expectContains(detail, "First blocker:")
    try expectContains(detail, "resource_inputs")
    try expectContains(detail, "missing_required_value")
    try expectContains(detail, "provide_MESHY_API_KEY")
    try expectContains(detail, "make final-resources-preflight")
    try expectContains(detail, "commands_run=false")
}

private func testDevicePreflightMarksReadyFinalClosurePacket() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: readyFinalClosurePacketReport()
    )
    let detail = summary.item(id: "final_launch_closure_packet")?.detail ?? ""

    try expectEqual(summary.item(id: "final_launch_closure_packet")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "sections 6")
    try expectContains(detail, "blocked 0")
    try expectContains(detail, "cost consent 0")
    try expectContains(detail, "commands_run=false")
    try expectContains(detail, "live_calls=false")
}

private func testDevicePreflightShowsConfiguredEvidenceClosureSection() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            closurePacketConfiguredBundleStatus: "blocked",
            closurePacketConfiguredBundleCommand: "make configured-live-evidence-bundle",
            closurePacketConfiguredBundleDetail: "Build configured live evidence bundle after resource and provider evidence are ready."
        )
    )
    let detail = summary.item(id: "final_launch_closure_packet")?.detail ?? ""

    try expectEqual(summary.item(id: "final_launch_closure_packet")?.status, .blocked)
    try expectContains(detail, "configured_evidence_bundle")
    try expectContains(detail, "configured_live_evidence_bundle")
    try expectContains(detail, "make configured-live-evidence-bundle")
}

private func testDevicePreflightRedactsUnsafeFinalClosurePacket() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        closurePacketActionCommand: "make final-launch-closure-packet sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret",
        closurePacketActionDetail: "api_key=secret private_message: raw words https://checkout.example/pay",
        closurePacketFirstBlockerCommand: "make final-resources-preflight sk-blocker /Users/zhexu/private file:///tmp/private local-capture://blocker checkout_url Bearer token",
        closurePacketFirstBlockerDetail: "api_key=secret private_message: raw blocker words https://checkout.example/pay",
        closurePacketConfiguredBundleCommand: "make configured-live-evidence-bundle sk-configured /Users/zhexu/private file:///tmp/private local-capture://configured checkout_url Bearer token",
        closurePacketConfiguredBundleDetail: "api_key=secret private_message: raw configured words https://checkout.example/pay"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_launch_closure_packet")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "sk-blocker")
    try expectNotContains(text, "sk-configured")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
    try expectNotContains(text, "private_message")
}

private func testDevicePreflightWaitsForMissingFinalOperatorHandoff() throws {
    var report = finalDemoLaunchReport(overallStatus: "partial")
    report.finalOperatorHandoff = nil
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )

    try expectEqual(summary.item(id: "final_operator_handoff")?.status, .waiting)
    try expectContains(summary.item(id: "final_operator_handoff")?.detail ?? "", "not loaded")
}

private func testDevicePreflightBlocksOnFinalOperatorHandoffNextAction() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            finalOperatorHandoffStatus: "blocked",
            finalOperatorHandoffAction: "provide iOS deploy config and rerun mobile deploy preflight"
        )
    )
    let detail = summary.item(id: "final_operator_handoff")?.detail ?? ""

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_operator_handoff")?.status, .blocked)
    try expectContains(detail, "blocked")
    try expectContains(detail, "ready 4")
    try expectContains(detail, "blocked 1")
    try expectContains(detail, "provide iOS deploy config")
    try expectContains(detail, "local_final_acceptance")
    try expectContains(detail, "make final-acceptance-local")
    try expectContains(detail, "final_acceptance_readiness")
    try expectContains(detail, "commands_run=false")
}

private func testDevicePreflightMarksReadyFinalOperatorHandoff() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        )
    )
    let detail = summary.item(id: "final_operator_handoff")?.detail ?? ""

    try expectEqual(summary.item(id: "final_operator_handoff")?.status, .ready)
    try expectContains(detail, "ready")
    try expectContains(detail, "ready 7")
    try expectContains(detail, "blocked 0")
    try expectContains(detail, "commands_run=false")
    try expectContains(detail, "app_exec=false")
}

private func testDevicePreflightShowsLiveFinalOperatorHandoffConsent() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalOperatorHandoffStatus: "live",
            finalOperatorHandoffAction: "run configured final acceptance with live provider consent"
        )
    )
    let detail = summary.item(id: "final_operator_handoff")?.detail ?? ""

    try expectEqual(summary.item(id: "final_operator_handoff")?.status, .blocked)
    try expectContains(detail, "live")
    try expectContains(detail, "requires consent")
    try expectContains(detail, "configured_final_acceptance")
    try expectContains(detail, "allow-live-provider-calls")
}

private func testDevicePreflightRedactsUnsafeFinalOperatorHandoff() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        finalOperatorHandoffStatus: "blocked",
        finalOperatorHandoffAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token api_key=secret"
    )
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: report
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.item(id: "final_operator_handoff")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDevicePreflightBlocksAndRedactsFinalLaunchError() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalDemoLaunch: nil,
        finalDemoLaunchError: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.overallStatus, .blocked)
    try expectEqual(summary.item(id: "final_launch")?.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalLaunchMobileSummaryWaitsForMissingReport() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(report: nil, error: nil)

    try expectEqual(summary.overallStatus, .waiting)
    try expectContains(summary.title, "Final launch report")
    try expectContains(summary.subtitle, "not loaded")
    try expectEqual(summary.phaseRows.count, 0)
    try expectEqual(summary.commandRows.count, 0)
}

private func testFinalLaunchMobileSummaryWaitsWithLaunchReceipt() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(report: nil, error: nil)

    try expectEqual(summary.launchReceiptRows.first, "Receipt: waiting for final launch report.")
}

private func testFinalLaunchMobileSummaryShowsAcceptanceBlockerReceipt() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "blocked",
            finalOperatorHandoffStatus: "blocked"
        ),
        error: nil
    )

    try expectContains(summary.launchReceiptRows[0], "Receipt: local launch blocked.")
    try expectContains(summary.launchReceiptRows[1], "Acceptance: 12 passed, 2 blocked, 0 failed.")
    try expectContains(summary.launchReceiptRows[2], "First blocker: mobile_deploy_preflight")
    try expectContains(summary.launchReceiptRows[2], "blocked_by_local_ios_deploy_config")
    try expectContains(summary.launchReceiptRows[3], "Live providers: consent required")
}

private func testFinalLaunchMobileSummaryShowsResourceBlockerReceipt() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalResourcesStatus: "blocked",
            finalResourcesItemsJSON: blockedFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            finalOperatorHandoffStatus: "blocked",
            finalOperatorHandoffAction: "copy final resources and rerun preflight"
        ),
        error: nil
    )

    try expectContains(summary.launchReceiptRows[2], "First blocker: MESHY_API_KEY")
    try expectContains(summary.launchReceiptRows[2], "missing")
}

private func testFinalLaunchMobileSummaryUsesTopLevelFirstBlockerReceipt() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        firstBlockerJSON: finalDemoLaunchTopLevelFirstBlockerJSON(),
        finalResourcesStatus: "blocked",
        finalResourcesItemsJSON: blockedFinalResourceItemsJSON(),
        finalAcceptanceStatus: "blocked",
        finalOperatorHandoffStatus: "blocked"
    )

    let blocker = try require(report.firstBlocker, "missing final demo launch first blocker")
    try expectEqual(blocker.id, "apply_final_resources")
    try expectEqual(blocker.label, "Apply final resources")
    try expectEqual(blocker.status, "missing")
    try expectEqual(blocker.classification, "final_demo_launch_phase")
    try expectEqual(blocker.command, "make final-apply-resources")
    try expectEqual(blocker.source, "final_demo_launch_phase")
    try expectEqual(blocker.sourceId, "apply_final_resources")

    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)

    try expectContains(
        summary.launchReceiptRows[2],
        "First blocker: apply_final_resources missing final_demo_launch_phase"
    )
    try expectContains(summary.launchReceiptRows[2], "make final-apply-resources")
    try expectContains(summary.launchReceiptRows[2], "one-file backend and iOS final demo handoff")
}

private func testFinalLaunchMobileSummaryShowsFinalDemoLaunchNextAction() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        firstBlockerJSON: finalDemoLaunchTopLevelFirstBlockerJSON(),
        nextActionJSON: finalDemoLaunchTopLevelNextActionJSON(),
        finalResourcesStatus: "blocked",
        finalResourcesItemsJSON: blockedFinalResourceItemsJSON(),
        finalAcceptanceStatus: "blocked",
        finalOperatorHandoffStatus: "blocked"
    )

    let action = try require(report.nextAction, "missing final demo launch next action")
    try expectEqual(action.id, "apply_final_resources")
    try expectEqual(action.source, "first_blocker")
    try expectEqual(action.sourceId, "apply_final_resources")
    try expectEqual(action.validationCommand, "make final-demo-launch-local")

    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)

    try expectContains(
        summary.launchReceiptRows[2],
        "Next action: apply_final_resources missing final_demo_launch_phase"
    )
    try expectContains(summary.launchReceiptRows[2], "make final-apply-resources")
    try expectContains(summary.launchReceiptRows[2], "one-file backend and iOS final demo handoff")
    try expectContains(summary.launchReceiptRows[2], "make final-demo-launch-local")
    try expectContains(summary.launchReceiptRows[3], "First blocker: apply_final_resources")
}

private func testFinalLaunchMobileSummaryShowsReadyConfiguredReceipt() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    try expectEqual(summary.launchReceiptRows[0], "Receipt: configured launch ready.")
    try expectEqual(summary.launchReceiptRows[2], "First blocker: none; final handoff ready.")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeLaunchReceipt() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "blocked",
            finalAcceptanceBlockerDetail: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
        ),
        error: nil
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)
    let receiptText = summary.launchReceiptRows.joined(separator: " ")

    try expectContains(receiptText, "[withheld]")
    try expectContains(text, "[withheld]")
    try expectNotContains(receiptText, "sk-test")
    try expectNotContains(receiptText, "/Users/")
    try expectNotContains(receiptText, "file:///")
    try expectNotContains(receiptText, "local-capture://")
    try expectNotContains(receiptText, "checkout")
    try expectNotContains(receiptText, "Bearer")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testLiveProviderConsentSummaryWaitsForProviderReadiness() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: nil,
        providerReadinessError: nil,
        finalLaunchReport: nil,
        finalLaunchError: nil
    )

    try expectEqual(summary.status, .waiting)
    try expectEqual(summary.canRunConfiguredAcceptance, false)
    try expectContains(summary.title, "waiting")
    try expectContains(summary.subtitle, "provider readiness")
    try expectContains(summary.rows.map(\.id).joined(separator: " "), "providers")
    try expectContains(summary.privacyNotes.joined(separator: " "), "backend-only")
}

private func testLiveProviderConsentSummaryBlocksMissingConfiguredProviders() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: missingProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "blocked",
            finalResourcesStatus: "blocked",
            finalResourcesItemsJSON: blockedFinalResourceItemsJSON(),
            resourceHandoffStatus: "blocked",
            resourceHandoffBackendStatus: "missing",
            resourceHandoffIOSStatus: "blocked",
            resourceHandoffAction: "provide MESHY_API_KEY"
        ),
        finalLaunchError: nil
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.status, .blocked)
    try expectEqual(summary.canRunConfiguredAcceptance, false)
    try expectEqual(summary.consentFlag, "--allow-live-provider-calls")
    try expectContains(text, "MESHY_API_KEY")
    try expectContains(text, "OPENAI_API_KEY")
    try expectContains(text, "consent required")
    try expectContains(text, "no live calls by default")
    try expectContains(text, "Resource handoff blocked")
}

private func testLiveProviderConsentSummaryShowsReadyConfiguredConsent() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        finalLaunchError: nil
    )
    let rowText = summary.rows.map { "\($0.label) \($0.detail)" }.joined(separator: " ")

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.canRunConfiguredAcceptance, true)
    try expectEqual(summary.consentFlag, "--allow-live-provider-calls")
    try expectContains(summary.title, "ready")
    try expectContains(rowText, "Meshy")
    try expectContains(rowText, "OpenAI")
    try expectContains(rowText, "print")
    try expectContains(rowText, "Final resources ready")
    try expectContains(summary.privacyNotes.joined(separator: " "), "does not call live providers by default")
}

private func testLiveProviderConsentSummaryShowsReadyLiveEvidence() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        finalLaunchError: nil
    )

    let row: LiveProviderConsentRow = try require(
        summary.rows.first { $0.id == "live_evidence" },
        "missing live evidence row"
    )

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.canRunConfiguredAcceptance, true)
    try expectEqual(row.status, .ready)
    try expectEqual(row.label, "Live evidence")
    try expectContains(row.detail, "Live evidence ready")
    try expectContains(row.detail, "ready 5")
}

private func testLiveProviderConsentSummaryShowsConfiguredBundleRow() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidenceBundleStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        finalLaunchError: nil
    )
    let row: LiveProviderConsentRow = try require(
        summary.rows.first { $0.id == "configured_bundle" },
        "missing configured bundle row"
    )

    try expectEqual(summary.status, .ready)
    try expectEqual(summary.canRunConfiguredAcceptance, true)
    try expectEqual(row.label, "Configured bundle")
    try expectEqual(row.status, .ready)
    try expectContains(row.detail, "Configured bundle ready")
    try expectContains(row.detail, "evidence ready 5")
}

private func testLiveProviderConsentSummaryBlocksConfiguredAcceptanceWithoutBundle() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            liveProviderEvidenceStatus: "ready",
            configuredEvidenceBundleStatus: "blocked",
            configuredEvidenceBundleBlockerDetail: "Final resource fill guide is blocked before configured evidence bundle.",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        finalLaunchError: nil
    )
    let row: LiveProviderConsentRow = try require(
        summary.rows.first { $0.id == "configured_bundle" },
        "missing configured bundle row"
    )

    try expectEqual(summary.status, .blocked)
    try expectEqual(summary.canRunConfiguredAcceptance, false)
    try expectEqual(row.status, .blocked)
    try expectContains(row.detail, "final_resource_fill_guide")
    try expectContains(row.detail, "Final resource fill guide is blocked")
}

private func testLiveProviderConsentSummaryBlocksMissingLiveEvidence() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            finalAcceptanceStatus: "ready",
            liveProviderEvidenceStatus: "blocked",
            liveProviderEvidenceBlockerDetail: "Core real providers are not ready for live evidence.",
            liveProviderEvidenceFirstID: "provider_handoff",
            liveProviderEvidenceFirstLabel: "Provider handoff",
            liveProviderEvidenceFirstStatus: "blocked",
            liveProviderEvidenceFirstClassification: "report_not_ready",
            liveProviderEvidenceCommand: "make provider-handoff",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready",
            iosDeployRunbookStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        finalLaunchError: nil
    )

    let row: LiveProviderConsentRow = try require(
        summary.rows.first { $0.id == "live_evidence" },
        "missing live evidence row"
    )

    try expectEqual(summary.status, .blocked)
    try expectEqual(summary.canRunConfiguredAcceptance, false)
    try expectEqual(row.status, .blocked)
    try expectContains(row.detail, "provider_handoff")
    try expectContains(row.detail, "Core real providers are not ready for live evidence.")
}

private func testLiveProviderConsentSummaryRedactsUnsafeLiveEvidenceBlocker() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: readyConfiguredProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "blocked",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON(),
            liveProviderEvidenceStatus: "blocked",
            liveProviderEvidenceBlockerDetail: (
                "Authorization Bearer sk-live /Users/zhexu/private "
                    + "/tmp/private file:///tmp/private.glb checkout_url https://pay.example/order"
            ),
            liveProviderEvidenceFirstID: "provider_handoff",
            liveProviderEvidenceFirstLabel: "Provider handoff",
            liveProviderEvidenceFirstStatus: "blocked",
            liveProviderEvidenceFirstClassification: "report_not_ready",
            liveProviderEvidenceCommand: "make provider-handoff",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready"
        ),
        finalLaunchError: nil
    )

    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-live")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "/tmp/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testLiveProviderConsentSummaryRedactsUnsafeText() throws {
    let summary = LiveProviderConsentSummaryBuilder.build(
        providerReadiness: ProviderReadinessResponse(
            overallDemoReady: false,
            overallRealReady: false,
            providers: [
                ProviderReadinessItem(
                    kind: "three_d",
                    selectedProvider: "meshy sk-test",
                    status: "Authorization Bearer token /Users/zhexu",
                    isDemoReady: false,
                    isRealProviderReady: false,
                    missingEnv: ["MESHY_API_KEY", "api_key=secret"],
                    notes: ["raw_context: private message local-capture://cap"]
                ),
            ]
        ),
        providerReadinessError: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        finalLaunchReport: finalDemoLaunchReport(
            mode: "configured",
            overallStatus: "blocked",
            finalResourcesStatus: "blocked",
            finalResourcesAction: "api_key=secret checkout_url=https://pay.example/private",
            resourceHandoffAction: "provide sk-test /Users/zhexu/private"
        ),
        finalLaunchError: "Bearer sk-test /tmp/private checkout_url"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.status, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "/tmp/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
    try expectNotContains(text, "raw_context")
    try expectNotContains(text, "api_key")
}

private func testFinalLaunchMobileSummaryBuildsPartialOperatorStatus() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "partial",
            finalResourcesStatus: "missing",
            finalResourcesAction: "run make final-resource-init"
        ),
        error: nil
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectContains(summary.title, "Final launch partial")
    try expectContains(summary.subtitle, "ready 4")
    try expectEqual(summary.phaseRows.first?.id, "backend_device_server")
    try expectEqual(summary.phaseRows.first?.status, .ready)
    try expectContains(summary.phaseRows.first?.detail ?? "", "make backend-device-demo")
    try expectContains(summary.phaseRows.last?.detail ?? "", "Launch report partial")
    try expectContains(summary.resourceActions.first ?? "", "run make final-resource-init")
    try expectContains(summary.commandRows.first ?? "", "make backend-device-demo")
    try expectContains(summary.notes.joined(separator: " "), "read-only")
}

private func testDecodesFinalDemoLaunchTopLevelStatus() throws {
    let report = finalDemoLaunchReport(
        status: "blocked",
        overallStatus: "partial"
    )

    try expectEqual(report.status, "blocked")
    try expectEqual(report.overallStatus, "partial")
}

private func testFinalLaunchMobileSummaryPrefersTopLevelStatus() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            status: "blocked",
            overallStatus: "partial"
        ),
        error: nil
    )

    try expectEqual(summary.overallStatus, .blocked)
    try expectContains(summary.title, "Final launch blocked")
    try expectContains(summary.launchReceiptRows.first ?? "", "launch blocked")
}

private func testFinalLaunchMobileSummaryFallsBackToOverallStatus() throws {
    let legacyPayload = finalDemoLaunchPayload(
        includeStatus: false,
        overallStatus: "ready"
    )
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: legacyPayload
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)

    try expectEqual(report.status, nil)
    try expectEqual(summary.overallStatus, .ready)
    try expectContains(summary.title, "Final launch ready")
}

private func testFinalLaunchMobileSummaryPrioritizesConfiguredAcceptanceCommand() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            mode: "configured",
            commands: [
                "make final-resource-requirements",
                "make final-resources-preflight",
                "make final-resource-apply-preview",
                "make final-apply-resources",
                "make final-acceptance-configured",
                "make mobile-deploy-preflight",
            ]
        ),
        error: nil
    )

    try expectEqual(summary.commandRows.count, 4)
    try expectEqual(summary.commandRows.first, "make final-acceptance-configured")
    try expectTrue(summary.commandRows.contains("make final-resource-requirements"))
    try expectFalse(summary.commandRows.contains("make final-apply-resources"))
}

private func testDecodesFinalResourcesPreflightItemsFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            finalResourcesStatus: "blocked",
            finalResourcesItemsJSON: blockedFinalResourceItemsJSON()
        )
    )

    let preflight = try require(report.finalResourcesPreflight, "missing final resources preflight")
    try expectEqual(preflight.items.count, 3)
    try expectEqual(preflight.items[0].id, "MESHY_API_KEY")
    try expectEqual(preflight.items[0].status, "missing")
    try expectTrue(preflight.items[0].required)
    try expectEqual(preflight.items[2].classification, "loopback_url")
}

private func testDecodesFinalResourceAutoBackendURLHandoffFields() throws {
    let applyNote = "Resolved by write_deploy_local_config.sh during final-apply-resources."
    let preflight = try PMFJSON.decoder.decode(
        FinalResourcesPreflightItem.self,
        from: Data("""
        {
          "id": "PMF_BACKEND_BASE_URL",
          "status": "ready",
          "required": true,
          "configured": true,
          "redacted": true,
          "classification": "apply_time_auto_url",
          "resolution_mode": "apply_time_auto",
          "apply_note": "\(applyNote)"
        }
        """.utf8)
    )
    let requirement = try PMFJSON.decoder.decode(
        FinalResourceRequirement.self,
        from: Data("""
        {
          "id": "PMF_BACKEND_BASE_URL",
          "label": "iPhone backend URL",
          "domain": "ios_deploy",
          "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
          "source_template": "PMF_BACKEND_BASE_URL=auto",
          "required": true,
          "secret": false,
          "configured": true,
          "status": "ready",
          "classification": "apply_time_auto_url",
          "unblocks": ["ios_deployable"],
          "validation_command": "make mobile-deploy-preflight",
          "notes": "Auto backend URL is resolved while applying resources.",
          "resolution_mode": "apply_time_auto",
          "apply_note": "\(applyNote)"
        }
        """.utf8)
    )
    let slot = try PMFJSON.decoder.decode(
        FinalResourceApplyPreviewSlot.self,
        from: Data("""
        {
          "id": "PMF_BACKEND_BASE_URL",
          "status": "ready",
          "required": true,
          "secret": false,
          "configured": true,
          "classification": "apply_time_auto_url",
          "redacted": true,
          "writes": ["PMF_BACKEND_BASE_URL"],
          "resolution_mode": "apply_time_auto",
          "apply_note": "\(applyNote)"
        }
        """.utf8)
    )

    try expectEqual(preflight.resolutionMode, "apply_time_auto")
    try expectEqual(preflight.applyNote, applyNote)
    try expectEqual(requirement.resolutionMode, "apply_time_auto")
    try expectEqual(requirement.applyNote, applyNote)
    try expectEqual(slot.resolutionMode, "apply_time_auto")
    try expectEqual(slot.applyNote, applyNote)
}

private func testFinalLaunchMobileSummaryShowsMissingResourceChecklist() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            finalResourcesStatus: "blocked",
            finalResourcesItemsJSON: blockedFinalResourceItemsJSON()
        ),
        error: nil
    )

    try expectEqual(summary.resourceChecklistRows.count, 3)
    try expectContains(summary.resourceChecklistRows[0], "MESHY_API_KEY")
    try expectContains(summary.resourceChecklistRows[0], "missing required")
    try expectContains(summary.resourceChecklistRows[1], "OPENAI_API_KEY")
    try expectContains(summary.resourceChecklistRows[2], "PMF_BACKEND_BASE_URL")
    try expectContains(summary.resourceChecklistRows[2], "loopback_url")
}

private func testFinalLaunchMobileSummaryShowsReadyResourceChecklist() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalResourcesItemsJSON: readyFinalResourceItemsJSON()
        ),
        error: nil
    )

    try expectEqual(summary.resourceChecklistRows.first, "Required final resources ready.")
}

private func testFinalLaunchMobileSummaryShowsAutoBackendURLHandoff() throws {
    var report = finalDemoLaunchReport(
        overallStatus: "ready",
        finalResourcesStatus: "ready",
        finalResourcesItemsJSON: autoFinalResourceItemsJSON(),
        finalResourceApplyPreviewStatus: "ready"
    )
    report.finalResourceRequirements = readyFinalResourceRequirementsReport()
    report.finalResourceApplyPreview = readyFinalResourceApplyPreviewReport()
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = (
        summary.resourceChecklistRows
            + summary.resourceRequirementRows
            + summary.applyPreviewRows
    ).joined(separator: " ")

    try expectContains(text, "PMF_BACKEND_BASE_URL")
    try expectContains(text, "apply_time_auto")
    try expectContains(text, "write_deploy_local_config.sh")
    try expectContains(text, "final-apply-resources")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeResourceChecklist() throws {
    let unsafeItems = """
    [
      {
        "id": "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        "status": "blocked",
        "required": true,
        "configured": false,
        "redacted": false,
        "classification": "api_key=secret /Users/zhexu/private checkout_url",
        "apply_note": "Bearer token /Users/zhexu/private checkout_url"
      }
    ]
    """
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            finalResourcesStatus: "blocked",
            finalResourcesItemsJSON: unsafeItems
        ),
        error: nil
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
}

private func testDecodesFinalResourceRequirementsFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    let requirements = try require(
        report.finalResourceRequirements,
        "missing final resource requirements"
    )

    try expectEqual(requirements.kind, "final_resource_requirements_report")
    try expectEqual(requirements.status, "blocked")
    let firstBlocker = try require(
        requirements.firstBlocker,
        "missing final resource requirements first blocker"
    )
    try expectEqual(firstBlocker.id, "MESHY_API_KEY")
    try expectEqual(firstBlocker.status, "missing")
    try expectEqual(firstBlocker.classification, "missing_required_value")
    try expectEqual(firstBlocker.command, "provide MESHY_API_KEY in final-resources.env")
    try expectEqual(firstBlocker.domain, "backend_provider")
    try expectEqual(firstBlocker.validationCommand, "make final-resources-preflight")
    try expectEqual(requirements.nextAction?.id, "MESHY_API_KEY")
    try expectEqual(requirements.nextAction?.source, "first_blocker")
    try expectEqual(requirements.summary.required, 5)
    try expectEqual(requirements.summary.secret, 4)
    try expectEqual(requirements.requirements.count, 2)
    try expectEqual(requirements.requirementsById["MESHY_API_KEY"]?.secret, true)
    try expectEqual(requirements.requirementsById["MESHY_API_KEY"]?.status, "missing")
    try expectEqual(
        requirements.requirementsById["MESHY_API_KEY"]?.destination,
        "services/backend/.local/final-resources.env"
    )
    try expectEqual(
        requirements.requirementsById["PMF_BACKEND_BASE_URL"]?.classification,
        "loopback_url"
    )
    try expectEqual(
        requirements.validationCommands.first,
        "make final-resource-requirements"
    )
    try expectFalse(requirements.safety.providerSecretsInReport)
    try expectFalse(requirements.safety.liveProviderCalls)
}

private func testFinalLaunchMobileSummaryShowsBlockedResourceRequirements() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.resourceRequirementRows.joined(separator: " ")

    try expectContains(text, "Resource requirements blocked")
    try expectContains(text, "required 5")
    try expectContains(text, "secret 4")
    try expectContains(text, "MESHY_API_KEY")
    try expectContains(text, "missing")
    try expectContains(text, "PMF_BACKEND_BASE_URL")
    try expectContains(text, "loopback_url")
    try expectContains(text, "provide MESHY_API_KEY in final-resources.env")
    try expectContains(text, "Backend-only secret for live Meshy 3D generation.")
    try expectContains(text, "make final-resource-requirements")
}

private func testFinalLaunchMobileSummaryShowsResourceRequirementsNextAction() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.resourceRequirementRows.joined(separator: " ")

    try expectContains(text, "Next input: MESHY_API_KEY missing")
    try expectContains(text, "provide MESHY_API_KEY in final-resources.env")
    try expectContains(text, "services/backend/.local/final-resources.env")
    try expectContains(text, "make final-resources-preflight")
}

private func testDecodesFinalResourceFillGuideFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    let guide = try require(
        report.finalResourceFillGuide,
        "missing final resource fill guide"
    )

    try expectEqual(guide.kind, "final_resource_fill_guide_report")
    try expectEqual(guide.status, "blocked")
    try expectEqual(guide.summary.requiredInputs, 5)
    try expectEqual(guide.summary.optionalInputs, 5)
    try expectEqual(guide.summary.configuredInputs, 3)
    try expectEqual(guide.summary.secretInputs, 4)
    try expectEqual(guide.requiredInputs.first?.id, "MESHY_API_KEY")
    try expectEqual(guide.requiredInputs.first?.displayValue, "<secret: fill locally>")
    try expectEqual(
        guide.requiredInputs.first?.inputSource,
        "services/backend/.local/final-resources.env"
    )
    try expectEqual(
        guide.commands.first,
        "make final-resource-requirements"
    )
    let firstBlocker = try require(
        guide.firstBlocker,
        "missing final resource fill guide first blocker"
    )
    try expectEqual(firstBlocker.id, "MESHY_API_KEY")
    try expectEqual(firstBlocker.command, "fill MESHY_API_KEY in services/backend/.local/final-resources.env")
    try expectEqual(firstBlocker.inputSource, "services/backend/.local/final-resources.env")
    try expectEqual(firstBlocker.validationCommand, "make final-resources-preflight")
    try expectFalse(guide.safety.writesBackendEnv)
    try expectFalse(guide.safety.liveProviderCalls)
}

private func testFinalLaunchMobileSummaryShowsResourceFillGuide() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.resourceFillGuideRows.joined(separator: " ")

    try expectContains(
        text,
        "Fill guide blocked: required 5, optional 5, configured 3, secret 4."
    )
    try expectContains(
        text,
        "MESHY_API_KEY: missing | services/backend/.local/final-resources.env | make final-resources-preflight"
    )
    try expectContains(text, "First blocker: MESHY_API_KEY missing")
    try expectContains(text, "fill MESHY_API_KEY in services/backend/.local/final-resources.env")
    try expectContains(text, "Command: make final-resource-requirements")
    try expectContains(
        text,
        "Safety: writes=false live_calls=false global_mutation=false"
    )
}

private func testDecodesFinalResourceApplyPreviewFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    let preview = try require(
        report.finalResourceApplyPreview,
        "missing final resource apply preview"
    )

    try expectEqual(preview.kind, "final_resource_apply_preview_report")
    try expectEqual(preview.status, "missing")
    try expectEqual(preview.summary.writeTargets, 2)
    try expectEqual(preview.writeTargetsById["backend_env"]?.destination, "services/backend/.env")
    try expectEqual(
        preview.writeTargetsById["ios_deploy_config"]?.destination,
        "apps/mobile/ios/Config/Deployment.local.xcconfig"
    )
    try expectEqual(preview.writeTargetsById["backend_env"]?.slots.first?.id, "MESHY_API_KEY")
    try expectEqual(preview.writeTargetsById["backend_env"]?.slots.first?.secret, true)
    try expectEqual(preview.writeTargetsById["backend_env"]?.slots.first?.writes, ["MESHY_API_KEY"])
    let firstBlocker = try require(
        preview.firstBlocker,
        "missing final resource apply preview first blocker"
    )
    try expectEqual(firstBlocker.id, "backend_env")
    try expectEqual(firstBlocker.command, "make final-apply-resources")
    try expectEqual(firstBlocker.blockedBy, ["MESHY_API_KEY"])
    try expectEqual(firstBlocker.validationCommand, "make final-resources-preflight")
    try expectEqual(preview.commands.first, "make final-resource-apply-preview")
    try expectFalse(preview.safety.writesBackendEnv)
    try expectFalse(preview.safety.writesIosDeployConfig)
    try expectFalse(preview.safety.runsShellWriters)
}

private func testFinalLaunchMobileSummaryShowsResourceApplyPreview() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.applyPreviewRows.joined(separator: " ")

    try expectContains(text, "Apply preview missing")
    try expectContains(text, "targets 2")
    try expectContains(text, "backend_env")
    try expectContains(text, "services/backend/.env")
    try expectContains(text, "First blocker: backend_env missing")
    try expectContains(text, "blocked by MESHY_API_KEY")
    try expectContains(text, "ios_deploy_config")
    try expectContains(text, "MESHY_API_KEY")
    try expectContains(text, "make final-resource-apply-preview")
}

private func testDecodesFinalExternalActionLedgerFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    let ledger = try require(
        report.finalExternalActionLedger,
        "missing final external action ledger"
    )

    try expectEqual(ledger.kind, "final_external_action_ledger_report")
    try expectEqual(ledger.status, "blocked")
    try expectEqual(ledger.summary.groups, 5)
    try expectEqual(ledger.summary.actions, 27)
    try expectEqual(ledger.summary.requiresCostConsent, 5)
    try expectEqual(ledger.actionGroups.first?.id, "resource_inputs")
    try expectEqual(ledger.actionGroups.first?.summary.missing, 5)
    try expectEqual(ledger.actionsById["provide_MESHY_API_KEY"]?.secret, true)
    try expectEqual(ledger.actionsById["run_xcode_build_gate"]?.global, true)
    try expectEqual(ledger.operatorSequence.first, "make final-resource-requirements")
    try expectFalse(ledger.safety.commandsRun)
    try expectFalse(ledger.safety.globalMutation)
    try expectTrue(ledger.safety.requiresCostConsentForLiveActions)
}

private func testFinalLaunchMobileSummaryShowsExternalActionLedger() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.externalActionLedgerRows.joined(separator: " ")

    try expectContains(text, "External actions blocked")
    try expectContains(text, "groups 5")
    try expectContains(text, "resource_inputs: blocked")
    try expectContains(text, "global_machine_actions: manual")
    try expectContains(text, "live cost consent true")
    try expectContains(text, "make final-resource-requirements")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeExternalActionLedger() throws {
    let report = finalDemoLaunchReport(
        externalActionLedgerCommand: (
            "make final-external-action-ledger sk-test /Users/zhexu/private "
                + "file:///tmp/private local-capture://cap checkout_url Bearer token"
        ),
        externalActionLedgerDetail: (
            "api_key=secret private_message: raw words https://checkout.example/pay"
        )
    )

    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = summary.externalActionLedgerRows.joined(separator: " ")

    try expectFalse(text.contains("sk-test"))
    try expectFalse(text.contains("/Users/"))
    try expectFalse(text.contains("file:///"))
    try expectFalse(text.contains("local-capture://"))
    try expectFalse(text.contains("checkout_url"))
    try expectFalse(text.contains("api_key=secret"))
    try expectFalse(text.contains("private_message"))
    try expectContains(text, "[withheld]")
}

private func testDecodesFinalLaunchClosurePacketFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    let packet = try require(
        report.finalLaunchClosurePacket,
        "missing final launch closure packet"
    )

    try expectEqual(packet.kind, "final_launch_closure_packet_report")
    try expectEqual(packet.status, "blocked")
    try expectEqual(packet.summary.sections, 6)
    try expectEqual(packet.summary.requiresCostConsent, 5)
    let firstBlocker = try require(packet.firstBlocker, "missing closure packet first blocker")
    try expectEqual(firstBlocker.id, "resource_inputs")
    try expectEqual(firstBlocker.label, "Resource inputs")
    try expectEqual(firstBlocker.status, "blocked")
    try expectEqual(firstBlocker.classification, "missing_required_value")
    try expectEqual(firstBlocker.command, "make final-resources-preflight")
    try expectEqual(
        firstBlocker.detail,
        "Backend-only secret for live Meshy 3D generation."
    )
    try expectEqual(firstBlocker.sectionId, "resource_inputs")
    try expectEqual(firstBlocker.actionId, "provide_MESHY_API_KEY")
    try expectEqual(packet.sections.first?.id, "resource_inputs")
    try expectEqual(packet.sections.first?.firstAction.id, "provide_MESHY_API_KEY")
    try expectEqual(
        packet.sectionsById["device_evidence"]?.command,
        "make ios-device-launch-rehearsal"
    )
    try expectEqual(packet.sectionsById["live_provider_consent"]?.requiresCostConsent, true)
    let configuredBundleSection = try require(
        packet.sectionsById["configured_evidence_bundle"],
        "missing configured evidence bundle closure section"
    )
    try expectEqual(configuredBundleSection.command, "make configured-live-evidence-bundle")
    try expectEqual(configuredBundleSection.firstAction.id, "configured_live_evidence_bundle")
    try expectEqual(
        configuredBundleSection.firstAction.command,
        "make configured-live-evidence-bundle"
    )
    try expectFalse(configuredBundleSection.requiresCostConsent)
    try expectFalse(configuredBundleSection.liveProviderCall)
    try expectFalse(packet.safety.commandsRun)
    try expectFalse(packet.safety.globalMutation)
    try expectFalse(packet.safety.liveProviderCalls)
    try expectTrue(packet.safety.describesGlobalActions)
}

private func testFinalLaunchMobileSummaryShowsFinalLaunchClosurePacket() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(),
        error: nil
    )
    let text = summary.closurePacketRows.joined(separator: " ")

    try expectContains(text, "Final closure blocked")
    try expectContains(text, "First blocker: resource_inputs blocked missing_required_value")
    try expectContains(text, "resource_inputs")
    try expectContains(text, "provide_MESHY_API_KEY")
    try expectContains(text, "make final-resources-preflight")
    try expectContains(text, "Backend-only secret for live Meshy 3D generation.")
    try expectContains(text, "configured_evidence_bundle")
    try expectContains(text, "configured_live_evidence_bundle")
    try expectContains(text, "make configured-live-evidence-bundle")
    try expectContains(text, "cost consent")
    try expectContains(text, "commands_run=false global=false live_calls=false")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeFinalLaunchClosurePacket() throws {
    let report = finalDemoLaunchReport(
        closurePacketActionCommand: (
            "make final-launch-closure-packet sk-test /Users/zhexu/private "
                + "file:///tmp/private local-capture://cap checkout_url Bearer token"
        ),
        closurePacketActionDetail: (
            "api_key=secret private_message: raw words https://checkout.example/pay"
        ),
        closurePacketFirstBlockerCommand: (
            "make final-resources-preflight sk-blocker /Users/zhexu/private "
                + "file:///tmp/private local-capture://blocker checkout_url Bearer token"
        ),
        closurePacketFirstBlockerDetail: (
            "api_key=secret private_message: raw blocker words https://checkout.example/pay"
        ),
        closurePacketConfiguredBundleCommand: (
            "make configured-live-evidence-bundle sk-configured /Users/zhexu/private "
                + "file:///tmp/private local-capture://configured checkout_url Bearer token"
        ),
        closurePacketConfiguredBundleDetail: (
            "api_key=secret private_message: raw configured words https://checkout.example/pay"
        )
    )

    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = summary.closurePacketRows.joined(separator: " ")

    try expectFalse(text.contains("sk-test"))
    try expectFalse(text.contains("/Users/"))
    try expectFalse(text.contains("file:///"))
    try expectFalse(text.contains("local-capture://"))
    try expectFalse(text.contains("checkout_url"))
    try expectFalse(text.contains("api_key=secret"))
    try expectFalse(text.contains("private_message"))
    try expectFalse(text.contains("sk-blocker"))
    try expectFalse(text.contains("raw blocker words"))
    try expectFalse(text.contains("sk-configured"))
    try expectFalse(text.contains("raw configured words"))
    try expectContains(text, "[withheld]")
}

private func testDecodesResourceHandoffFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            resourceHandoffStatus: "blocked",
            resourceHandoffBackendStatus: "missing",
            resourceHandoffIOSStatus: "blocked"
        )
    )

    let handoff = try require(report.resourceReport, "missing resource handoff report")
    try expectEqual(handoff.kind, "resource_handoff_report")
    try expectEqual(handoff.overallStatus, "blocked")
    try expectEqual(handoff.summary.missing, 4)
    try expectEqual(handoff.backend.destination, "services/backend/.env")
    try expectEqual(handoff.backend.items.first?.id, "MESHY_API_KEY")
    try expectEqual(handoff.backend.items.first?.requiredFor, "real text/image/multi-image 3D generation")
    try expectEqual(handoff.ios.destination, "apps/mobile/ios/Config/Deployment.local.xcconfig")
    try expectEqual(handoff.ios.items.first?.id, "PMF_BACKEND_BASE_URL")
    try expectFalse(handoff.safety.providerSecretsInReport)
    try expectFalse(handoff.safety.localPathsInReport)
}

private func testFinalLaunchMobileSummaryShowsMissingResourceHandoff() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            resourceHandoffStatus: "blocked",
            resourceHandoffBackendStatus: "missing",
            resourceHandoffIOSStatus: "blocked",
            resourceHandoffAction: "provide MESHY_API_KEY"
        ),
        error: nil
    )
    let overviewText = summary.resourceHandoffRows.joined(separator: " ")
    let backendText = summary.resourceHandoffBackendRows.joined(separator: " ")
    let iosText = summary.resourceHandoffIOSRows.joined(separator: " ")

    try expectEqual(
        summary.resourceHandoffRows.first,
        "Resource handoff blocked: ready 2, missing 4, blocked 1, manual 1."
    )
    try expectContains(overviewText, "Backend: services/backend/.env")
    try expectContains(overviewText, "iOS: apps/mobile/ios/Config/Deployment.local.xcconfig")
    try expectContains(overviewText, "provide MESHY_API_KEY")
    try expectContains(backendText, "MESHY_API_KEY: missing")
    try expectContains(backendText, "real text/image/multi-image 3D generation")
    try expectContains(iosText, "PMF_BACKEND_BASE_URL: blocked")
    try expectContains(iosText, "device-to-Mac backend calls")
}

private func testFinalLaunchMobileSummaryShowsReadyResourceHandoff() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            resourceHandoffStatus: "ready",
            resourceHandoffBackendStatus: "ready",
            resourceHandoffIOSStatus: "ready",
            resourceHandoffAction: "final resource handoff ready"
        ),
        error: nil
    )

    try expectContains(summary.resourceHandoffRows.first ?? "", "Resource handoff ready")
    try expectContains(summary.resourceHandoffBackendRows.joined(separator: " "), "MESHY_API_KEY: ready")
    try expectContains(summary.resourceHandoffBackendRows.joined(separator: " "), "OPENAI_API_KEY: ready")
    try expectContains(summary.resourceHandoffIOSRows.joined(separator: " "), "PMF_BACKEND_BASE_URL: ready")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff() throws {
    let report = finalDemoLaunchReport(
        resourceHandoffStatus: "blocked",
        resourceHandoffBackendStatus: "missing",
        resourceHandoffIOSStatus: "blocked",
        resourceHandoffAction: "provide sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        resourceHandoffDestination: "/Users/zhexu/private/.env"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDecodesFinalAcceptanceReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(finalAcceptanceStatus: "blocked")
    )

    let readiness = try require(
        report.finalAcceptanceReadiness,
        "missing final acceptance readiness"
    )
    try expectEqual(readiness.kind, "final_acceptance_readiness_report")
    try expectEqual(readiness.status, "blocked")
    try expectEqual(readiness.sourceFile.path, "services/backend/.local/final-acceptance-local.json")
    try expectEqual(readiness.sourceFile.exists, true)
    try expectEqual(readiness.summary.passed, 12)
    try expectEqual(readiness.summary.blocked, 2)
    try expectEqual(readiness.blockers.first?.id, "mobile_deploy_preflight")
    try expectEqual(readiness.blockers.first?.classification, "blocked_by_local_ios_deploy_config")
    try expectContains(readiness.operatorActions.first ?? "", "provide iOS deploy config")
    try expectFalse(readiness.safety.commandsRun)
}

private func testDecodesFinalAcceptanceFreshnessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            finalAcceptanceStatus: "blocked",
            finalAcceptanceFreshnessStatus: "stale",
            finalAcceptanceFreshnessClassification: "stale_report"
        )
    )
    let freshness = try require(report.finalAcceptanceReadiness?.freshness, "missing freshness")

    try expectEqual(freshness.status, "stale")
    try expectEqual(freshness.classification, "stale_report")
    try expectEqual(freshness.checkedAgainst, "git_head")
}

private func testFinalLaunchMobileSummaryWaitsForFinalAcceptanceReadiness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(finalAcceptanceStatus: "missing"),
        error: nil
    )

    try expectEqual(summary.acceptanceRows.first, "Run local final acceptance to create the latest readiness report.")
}

private func testFinalLaunchMobileSummaryShowsStaleFinalAcceptanceFreshness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalAcceptanceStatus: "blocked",
            finalAcceptanceFreshnessStatus: "stale",
            finalAcceptanceFreshnessClassification: "stale_report"
        ),
        error: nil
    )

    try expectContains(summary.launchReceiptRows[1], "stale_report")
    try expectContains(summary.acceptanceRows.first ?? "", "stale_report")
}

private func testFinalLaunchMobileSummaryShowsBlockedFinalAcceptance() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(finalAcceptanceStatus: "blocked"),
        error: nil
    )

    try expectEqual(summary.acceptanceRows.count, 2)
    try expectContains(summary.acceptanceRows[0], "mobile_deploy_preflight")
    try expectContains(summary.acceptanceRows[0], "blocked_by_local_ios_deploy_config")
    try expectContains(summary.acceptanceRows[0], "make mobile-deploy-preflight")
    try expectContains(summary.acceptanceRows[1], "mobile_xcode_build")
    try expectContains(summary.acceptanceRows[1], "blocked_by_apple_sdk_license")
}

private func testFinalLaunchMobileSummaryShowsReadyFinalAcceptance() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready"
        ),
        error: nil
    )

    try expectEqual(summary.overallStatus, .ready)
    try expectEqual(summary.acceptanceRows.first, "Final acceptance ready.")
}

private func testDecodesThreeDEvaluationReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(threeDEvaluationStatus: "ready")
    )

    let readiness = try require(
        report.threeDEvaluationReadiness,
        "missing 3D evaluation readiness"
    )
    try expectEqual(readiness.kind, "three_d_evaluation_readiness_report")
    try expectEqual(readiness.status, "ready")
    try expectEqual(readiness.summary.succeeded, 20)
    try expectEqual(readiness.summary.failed, 0)
    try expectEqual(readiness.coverage.inputModes.textPrompt, 20)
    try expectEqual(readiness.coverage.variantRoles["ios_scene_asset"], 20)
    try expectEqual(readiness.coverage.sceneLoadableCases, 20)
    try expectFalse(readiness.safety.commandsRun)
}

private func testFinalLaunchMobileSummaryShowsReadyThreeDEvaluation() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(threeDEvaluationStatus: "ready"),
        error: nil
    )

    try expectEqual(
        summary.threeDEvaluationRows.first,
        "3D evaluation ready: 20 cases, 20 scene-loadable."
    )
    try expectContains(summary.threeDEvaluationRows[1], "20 text")
    try expectContains(summary.threeDEvaluationRows[1], "ios_scene_asset 20")
}

private func testFinalLaunchMobileSummaryShowsBlockedThreeDEvaluation() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            threeDEvaluationStatus: "blocked",
            threeDEvaluationBlockerDetail: (
                "Meshy failed Authorization=Bearer test-secret raw_context: private "
                + "file:///Users/example/private.png data:image/png;base64,abc123 checkout_url"
            )
        ),
        error: nil
    )
    let text = summary.threeDEvaluationRows.joined(separator: " ")

    try expectContains(text, "three_d_evaluation_failed")
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "test-secret")
    try expectNotContains(text, "raw_context:")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "data:image")
    try expectNotContains(text, "checkout_url")
    try expectNotContains(text, "Bearer")
}

private func testDecodesVisualRegressionReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(visualRegressionStatus: "ready")
    )

    let readiness = try require(
        report.visualRegressionReadiness,
        "missing visual regression readiness"
    )
    try expectEqual(readiness.kind, "visual_regression_readiness_report")
    try expectEqual(readiness.status, "ready")
    try expectEqual(readiness.summary.passed, 1)
    try expectEqual(readiness.summary.failed, 0)
    try expectEqual(readiness.artifacts.first?.id, "p0.118_scene_load_proof")
    try expectFalse(readiness.safety.commandsRun)
}

private func testFinalLaunchMobileSummaryShowsReadyVisualRegression() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(visualRegressionStatus: "ready"),
        error: nil
    )

    try expectEqual(
        summary.visualRegressionRows.first,
        "Visual regression ready: 1 artifact passed, 0 failed."
    )
    try expectContains(
        summary.visualRegressionRows.joined(separator: " "),
        "p0.118_scene_load_proof"
    )
}

private func testFinalLaunchMobileSummaryShowsBlockedVisualRegression() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            visualRegressionStatus: "blocked",
            visualRegressionBlockerDetail: "unsafe screenshot text Authorization=Bearer test-secret"
        ),
        error: nil
    )
    let text = summary.visualRegressionRows.joined(separator: " ")

    try expectContains(text, "visual_regression_failed")
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "test-secret")
    try expectNotContains(text, "Bearer")
}

private func testFinalLaunchMobileSummaryShowsStaleVisualRegressionFreshness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            visualRegressionStatus: "blocked",
            visualRegressionFreshnessStatus: "stale",
            visualRegressionFreshnessClassification: "stale_report",
            visualRegressionBlockerClassification: "stale_report",
            visualRegressionBlockerDetail: "Visual regression report is older than current git revision."
        ),
        error: nil
    )
    let text = summary.visualRegressionRows.joined(separator: " ")

    try expectContains(text, "Visual regression freshness stale_report")
    try expectContains(text, "rerun local visual regression")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeVisualRegression() throws {
    let report = finalDemoLaunchReport(
        visualRegressionStatus: "blocked",
        visualRegressionBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://pay.example Bearer token"
        ),
        visualRegressionAction: "rerun make visual-regression-local sk-test /Users/zhexu/private"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
}

private func testDecodesLocalShowcaseSmokeFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(localShowcaseSmokeStatus: "succeeded")
    )

    let smoke = try require(
        report.localShowcaseSmoke,
        "missing local showcase smoke"
    )
    try expectEqual(smoke.kind, "local_showcase_smoke_report")
    try expectEqual(smoke.status, "succeeded")
    try expectEqual(smoke.summary.httpSteps, 6)
    try expectEqual(smoke.summary.npcTicks, 2)
    try expectEqual(smoke.summary.downloads, 3)
    try expectEqual(smoke.session.generatedAssetProvider, "local_stub")
    try expectEqual(smoke.session.generationInputMode, "multi_image")
    try expectEqual(smoke.session.sceneVariantFormat, "dae")
    try expectEqual(smoke.npc.completedSteps, 2)
    try expectEqual(smoke.print.quoteStatus, "draft_quote")
    try expectEqual(smoke.downloads.gameGlb.contentProof, "glTF")
    try expectFalse(smoke.safety.providerCalls)
    try expectTrue(smoke.safety.usesTemporaryStorage)
}

private func testFinalLaunchMobileSummaryShowsLocalShowcaseSmoke() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(localShowcaseSmokeStatus: "succeeded"),
        error: nil
    )
    let text = summary.localShowcaseSmokeRows.joined(separator: " ")

    try expectContains(text, "Local showcase smoke ready: HTTP 6, NPC ticks 2, downloads 3.")
    try expectContains(text, "3D local_stub via multi_image; scene dae.")
    try expectContains(text, "Print draft_quote; game glTF, scene COLLADA, print PK.")
    try expectContains(text, "provider_calls=false global=false temp_storage=true")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeLocalShowcaseSmoke() throws {
    let report = finalDemoLaunchReport(
        localShowcaseSmokeStatus: "failed",
        localShowcaseSmokeFailureDetail: (
            "Authorization=Bearer sk-local data:image/png;base64,AAAA "
            + "/Users/zhexu/private /tmp/private local-capture://cap checkout_url"
        )
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-local")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "/tmp/")
    try expectNotContains(text, "data:image")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDecodesLiveProviderEvidenceFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(liveProviderEvidenceStatus: "missing")
    )

    let evidence = try require(
        report.liveProviderEvidence,
        "missing live provider evidence"
    )
    try expectEqual(evidence.kind, "live_provider_evidence_report")
    try expectEqual(evidence.status, "missing")
    try expectEqual(evidence.summary.missing, 5)
    try expectEqual(evidence.summary.requiresLiveProviderConsent, 3)
    try expectEqual(evidence.evidence.first?.id, "provider_handoff")
    try expectFalse(evidence.safety.commandsRun)
}

private func testFinalLaunchMobileSummaryShowsReadyLiveProviderEvidence() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(liveProviderEvidenceStatus: "ready"),
        error: nil
    )
    let text = summary.liveProviderEvidenceRows.joined(separator: " ")

    try expectContains(text, "Live evidence ready: ready 5, missing 0, blocked 0, partial 0.")
    try expectContains(text, "Live provider consent commands: 3.")
}

private func testFinalLaunchMobileSummaryShowsMissingLiveProviderEvidence() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(liveProviderEvidenceStatus: "missing"),
        error: nil
    )
    let text = summary.liveProviderEvidenceRows.joined(separator: " ")

    try expectContains(text, "Live evidence missing: ready 0, missing 5, blocked 0, partial 0.")
    try expectContains(text, "provider_handoff: missing")
    try expectContains(text, "make live-provider-evidence")
}

private func testFinalLaunchMobileSummaryShowsBlockedLiveProviderEvidence() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            liveProviderEvidenceStatus: "blocked",
            liveProviderEvidenceBlockerDetail: "Meshy live evaluation failed"
        ),
        error: nil
    )
    let text = summary.liveProviderEvidenceRows.joined(separator: " ")

    try expectContains(text, "three_d_evaluation_configured: blocked report_not_ready")
    try expectContains(text, "Meshy live evaluation failed")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeLiveProviderEvidence() throws {
    let report = finalDemoLaunchReport(
        liveProviderEvidenceStatus: "blocked",
        liveProviderEvidenceBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://pay.example Bearer token"
        )
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
}

private func testDecodesConfiguredEvidencePlanFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(configuredEvidencePlanStatus: "blocked")
    )

    let plan = try require(
        report.finalConfiguredEvidencePlan,
        "missing configured evidence plan"
    )
    try expectEqual(plan.kind, "final_configured_evidence_plan_report")
    try expectEqual(plan.status, "blocked")
    try expectEqual(plan.summary.steps, 6)
    try expectEqual(plan.summary.consentRequired, 2)
    try expectEqual(plan.summary.plannedConsentSteps, 3)
    try expectEqual(plan.steps.first?.id, "three_d_evaluation_configured")
    try expectEqual(
        plan.stepsById["three_d_evaluation_configured"]?.requiresLiveProviderConsent,
        true
    )
    try expectFalse(plan.liveCallPolicy.liveCallsByDefault)
    try expectFalse(plan.safety.commandsRun)
    try expectFalse(plan.safety.liveProviderCalls)
}

private func testFinalLaunchMobileSummaryShowsConfiguredEvidencePlan() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(configuredEvidencePlanStatus: "blocked"),
        error: nil
    )
    let text = summary.configuredEvidencePlanRows.joined(separator: " ")

    try expectContains(
        text,
        "Configured evidence blocked: steps 6, ready 3, blocked 2, consent now 2, planned 3."
    )
    try expectContains(text, "three_d_evaluation_configured: blocked")
    try expectContains(text, "requires MESHY_API_KEY")
    try expectContains(text, "Consent flag: PMF_ALLOW_LIVE_PROVIDER_CALLS")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidencePlan() throws {
    let report = finalDemoLaunchReport(
        configuredEvidencePlanStatus: "blocked",
        configuredEvidencePlanBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://pay.example Bearer token"
        )
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
}

private func testDecodesConfiguredEvidenceBundleFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(configuredEvidenceBundleStatus: "blocked")
    )

    let bundle = try require(
        report.configuredLiveEvidenceBundle,
        "missing configured evidence bundle"
    )
    try expectEqual(bundle.kind, "configured_live_evidence_bundle_report")
    try expectEqual(bundle.status, "blocked")
    try expectEqual(bundle.summary.evidenceFiles, 5)
    try expectEqual(bundle.summary.commands, 6)
    try expectEqual(bundle.currentBlocker?.id, "final_resource_fill_guide")
    try expectEqual(bundle.evidenceFiles.first?.id, "provider_handoff")
    try expectEqual(bundle.commandSequence.first?.id, "final_resource_fill_guide")
    try expectFalse(bundle.liveCallPolicy.liveCallsByDefault)
    try expectFalse(bundle.safety.commandsRun)
    try expectFalse(bundle.safety.liveProviderCalls)
}

private func testFinalLaunchMobileSummaryShowsConfiguredEvidenceBundle() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(configuredEvidenceBundleStatus: "blocked"),
        error: nil
    )
    let text = summary.configuredEvidenceBundleRows.joined(separator: " ")

    try expectContains(text, "Configured bundle blocked")
    try expectContains(text, "evidence ready 0, missing 5")
    try expectContains(text, "commands ready 3, blocked 2, consent 1")
    try expectContains(text, "final_resource_fill_guide: blocked")
    try expectContains(text, "make configured-live-evidence-bundle")
    try expectContains(text, "live calls by default no")
    try expectContains(text, "commands_run=false live_calls=false")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidenceBundle() throws {
    let report = finalDemoLaunchReport(
        configuredEvidenceBundleStatus: "blocked",
        configuredEvidenceBundleBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://checkout.example/pay "
            + "http://10.0.0.24:8080 Bearer token"
        )
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "10.0.0.24")
    try expectNotContains(text, "Bearer")
}

private func testDecodesPrintFulfillmentReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(printFulfillmentReadinessStatus: "partial")
    )

    let readiness = try require(
        report.printFulfillmentReadiness,
        "missing print fulfillment readiness"
    )
    try expectEqual(readiness.kind, "print_fulfillment_readiness_report")
    try expectEqual(readiness.status, "partial")
    try expectEqual(readiness.summary.ready, 4)
    try expectEqual(readiness.summary.partial, 1)
    try expectEqual(readiness.checks.first?.id, "print_quote_acceptance")
    try expectEqual(readiness.firstBlocker?.id, "configured_treatstock_quote")
    try expectFalse(readiness.safety.commandsRun)
    try expectFalse(readiness.safety.liveProviderCalls)
    try expectFalse(readiness.safety.paymentLinksInReport)
}

private func testFinalLaunchMobileSummaryShowsPrintFulfillmentReadiness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(printFulfillmentReadinessStatus: "partial"),
        error: nil
    )
    let text = summary.printFulfillmentReadinessRows.joined(separator: " ")

    try expectContains(text, "Print fulfillment partial: ready 4, partial 1, blocked 0.")
    try expectContains(text, "configured_treatstock_quote: partial")
    try expectContains(text, "make print-fulfillment-readiness")
}

private func testFinalLaunchMobileSummaryRedactsUnsafePrintFulfillmentReadiness() throws {
    let report = finalDemoLaunchReport(
        printFulfillmentReadinessStatus: "blocked",
        printFulfillmentReadinessBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://checkout.example/order "
            + "https://pay.example Bearer token"
        ),
        printFulfillmentReadinessAction: (
            "make print-fulfillment-readiness sk-test /Users/zhexu/private"
        )
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
}

private func testDecodesFinalShowcaseReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(finalShowcaseReadinessStatus: "partial")
    )

    let readiness = try require(
        report.finalShowcaseReadiness,
        "missing final showcase readiness"
    )
    try expectEqual(readiness.kind, "final_showcase_readiness_report")
    try expectEqual(readiness.status, "partial")
    try expectEqual(readiness.summary.partial, 3)
    try expectEqual(readiness.capabilities.first?.id, "ios_deployable")
    try expectEqual(readiness.firstBlocker?.id, "ios_deployable")
    try expectEqual(readiness.nextAction?.id, "ios_deployable")
    try expectEqual(readiness.nextAction?.source, "first_blocker")
    let bundle = try require(
        readiness.deviceActionBundle,
        "missing final showcase device action bundle"
    )
    try expectEqual(bundle.id, "ios_device_manual_actions")
    try expectEqual(bundle.summary.actions, 4)
    try expectEqual(bundle.summary.manual, 4)
    try expectEqual(bundle.summary.xcodeOrSigning, 1)
    try expectEqual(bundle.firstAction.id, "start_backend_device_demo")
    try expectEqual(bundle.firstAction.command, "make backend-device-demo")
    try expectEqual(
        try require(bundle.firstAction.evidenceDetail, "missing first action evidence detail"),
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    try expectEqual(bundle.actions[1].command, "make mobile-deploy-preflight")
    try expectEqual(try require(bundle.actions[1].evidenceStatus, "missing evidence status"), "blocked")
    try expectEqual(
        try require(bundle.actions[1].evidenceSource, "missing evidence source"),
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    try expectEqual(
        try require(bundle.actions[1].validationCommand, "missing validation command"),
        "make mobile-deploy-preflight-evidence"
    )
    try expectContains(
        try require(bundle.actions[1].evidenceDetail, "missing evidence detail"),
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    try expectEqual(
        try require(bundle.actions[2].evidenceStatus, "missing xcode evidence status"),
        "blocked"
    )
    try expectEqual(
        try require(bundle.actions[2].evidenceSource, "missing xcode evidence source"),
        "services/backend/.local/mobile-xcode-build-evidence.json"
    )
    try expectEqual(
        try require(bundle.actions[2].validationCommand, "missing xcode validation command"),
        "make mobile-xcode-build-evidence"
    )
    try expectContains(
        try require(bundle.actions[2].evidenceDetail, "missing xcode evidence detail"),
        "Apple SDK license agreement is not accepted."
    )
    try expectFalse(bundle.safety.commandsRun)
    try expectFalse(readiness.safety.commandsRun)
    try expectFalse(readiness.safety.liveProviderCalls)
}

private func testFinalLaunchMobileSummaryShowsFinalShowcaseReadiness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(finalShowcaseReadinessStatus: "partial"),
        error: nil
    )
    let text = summary.showcaseReadinessRows.joined(separator: " ")

    try expectContains(text, "Showcase readiness partial: ready 5, partial 3, blocked 0.")
    try expectContains(text, "ios_deployable: partial")
    try expectContains(text, "make ios-device-launch-rehearsal")
}

private func testFinalLaunchMobileSummaryShowsFinalShowcaseNextAction() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            finalShowcaseReadinessStatus: "blocked",
            finalShowcaseReadinessFirstBlockerDetail: (
                "iOS deploy runbook and device launch rehearsal must both be ready. "
                + "| Next device action: make backend-device-demo "
                + "| PMF_BACKEND_BASE_URL must be iPhone-reachable"
            )
        ),
        error: nil
    )
    let text = summary.showcaseReadinessRows.joined(separator: " ")

    try expectContains(text, "Next action: ios_deployable blocked")
    try expectContains(text, "make ios-device-launch-rehearsal")
    try expectContains(
        text,
        "iOS deploy runbook and device launch rehearsal must both be ready."
    )
    try expectContains(text, "Next device action: make backend-device-demo")
    try expectContains(text, "PMF_BACKEND_BASE_URL must be iPhone-reachable")
}

private func testFinalLaunchMobileSummaryShowsPriorityFinalShowcaseActions() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            finalShowcaseReadinessStatus: "blocked",
            finalShowcaseReadinessActions: [
                "final_rehearsal_local: final_acceptance_local: provide iOS deploy config",
                "final_rehearsal_local: final_acceptance_local: resolve Xcode build gate",
                "final_handoff_index: run make final-configured-preflight",
                "ios_device_launch_certificate: run make final-handoff-index",
                "run make live-provider-evidence after configured provider evidence files are refreshed",
                "run make final-resource-init",
                "make final-showcase-readiness",
                "extra action that should stay hidden",
            ]
        ),
        error: nil
    )
    let text = summary.showcaseReadinessRows.joined(separator: " ")

    try expectContains(text, "final_rehearsal_local: final_acceptance_local")
    try expectContains(text, "final_handoff_index: run make final-configured-preflight")
    try expectContains(text, "ios_device_launch_certificate: run make final-handoff-index")
    try expectContains(text, "run make live-provider-evidence")
    try expectContains(text, "run make final-resource-init")
    try expectContains(text, "make final-showcase-readiness")
    try expectNotContains(text, "extra action that should stay hidden")
    try expectEqual(summary.showcaseReadinessRows.count, 14)
}

private func testFinalLaunchMobileSummaryShowsFinalShowcaseDeviceActionBundle() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(finalShowcaseReadinessStatus: "blocked"),
        error: nil
    )
    let text = summary.showcaseReadinessRows.joined(separator: " ")

    try expectContains(text, "Device actions blocked: actions 4, manual 4, xcode 1.")
    try expectContains(text, "start_backend_device_demo: blocked")
    try expectContains(text, "make backend-device-demo")
    try expectContains(text, "make mobile-deploy-preflight")
    try expectContains(text, "PMF_BACKEND_BASE_URL must be iPhone-reachable")
    try expectContains(text, "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable")
    try expectContains(text, "make mobile-deploy-preflight-evidence")
    try expectContains(text, "evidence blocked")
    try expectContains(text, "make mobile-xcode-build-evidence")
    try expectContains(text, "commands_run=false")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeFinalShowcaseReadiness() throws {
    let report = finalDemoLaunchReport(
        finalShowcaseReadinessStatus: "blocked",
        finalShowcaseReadinessFirstBlockerDetail: (
            "sk-test /Users/zhexu/private file:///tmp/private "
            + "local-capture://cap checkout_url https://pay.example Bearer token"
        ),
        finalShowcaseReadinessAction: "make final-showcase-readiness sk-test /Users/zhexu/private"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
}

private func testDecodesNPCAgentEvaluationReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(npcEvaluationStatus: "ready")
    )

    let readiness = try require(
        report.npcAgentEvaluationReadiness,
        "missing NPC Agent evaluation readiness"
    )
    try expectEqual(readiness.kind, "npc_agent_evaluation_readiness_report")
    try expectEqual(readiness.status, "ready")
    try expectEqual(readiness.summary.succeeded, 6)
    try expectEqual(readiness.summary.failed, 0)
    try expectEqual(readiness.coverage.tickStepsCompleted, 12)
    try expectEqual(readiness.coverage.worldResolutionSteps, 12)
    try expectFalse(readiness.safety.commandsRun)
}

private func testFinalLaunchMobileSummaryShowsReadyNPCAgentEvaluation() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(npcEvaluationStatus: "ready"),
        error: nil
    )

    try expectEqual(
        summary.npcEvaluationRows.first,
        "NPC Agent evaluation ready: 6 cases, 12 ticks."
    )
    try expectContains(summary.npcEvaluationRows[1], "6 trace sets")
    try expectContains(summary.npcEvaluationRows[1], "12 world resolutions")
}

private func testFinalLaunchMobileSummaryShowsBlockedNPCAgentEvaluation() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            npcEvaluationStatus: "blocked",
            npcEvaluationBlockerDetail: "failed Authorization=Bearer test-secret private_message: raw"
        ),
        error: nil
    )
    let text = summary.npcEvaluationRows.joined(separator: " ")

    try expectContains(text, "npc_agent_evaluation_failed")
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "test-secret")
    try expectNotContains(text, "private_message:")
    try expectNotContains(text, "Bearer")
}

private func testDecodesFinalOperatorHandoffFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            finalOperatorHandoffStatus: "blocked",
            finalOperatorHandoffAction: "provide iOS deploy config and rerun mobile deploy preflight"
        )
    )

    let handoff = try require(
        report.finalOperatorHandoff,
        "missing final operator handoff"
    )
    try expectEqual(handoff.kind, "final_operator_handoff_report")
    try expectEqual(handoff.status, "blocked")
    try expectEqual(handoff.summary.blocked, 1)
    try expectEqual(handoff.summary.live, 0)
    try expectEqual(handoff.steps.first?.id, "local_final_acceptance")
    try expectEqual(handoff.steps.first?.source, "final_acceptance_readiness")
    try expectContains(handoff.nextActions.first ?? "", "provide iOS deploy config")
    try expectFalse(handoff.safety.commandsRun)
    try expectFalse(handoff.safety.commandExecutionFromApp)
}

private func testFinalLaunchMobileSummaryShowsHandoffNextActions() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            finalOperatorHandoffStatus: "blocked",
            finalOperatorHandoffAction: "provide iOS deploy config and rerun mobile deploy preflight"
        ),
        error: nil
    )

    try expectEqual(summary.handoffRows.count, 1)
    try expectContains(summary.handoffRows[0], "provide iOS deploy config")
}

private func testFinalLaunchMobileSummaryShowsReadyHandoff() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    try expectEqual(summary.handoffRows.first, "Final operator handoff ready.")
}

private func testDecodesIOSDeployRunbookFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            iosDeployRunbookStatus: "partial",
            iosDeployRunbookSlotStatus: "missing"
        )
    )

    let runbook = try require(report.iosDeployRunbook, "missing iOS deploy runbook")
    try expectEqual(runbook.kind, "ios_deploy_runbook_report")
    try expectEqual(runbook.mode, "local")
    try expectEqual(runbook.status, "partial")
    try expectEqual(runbook.inputSlots.first?.id, "backend_base_url")
    try expectEqual(runbook.inputSlots.first?.required, true)
    try expectEqual(runbook.inputSlots.first?.configured, false)
    try expectEqual(runbook.commandSequence.first?.id, "mobile_deploy_preflight")
    try expectEqual(runbook.commandSequence.first?.requiresConsent, false)
    try expectFalse(runbook.safety.commandsRun)
    try expectFalse(runbook.safety.providerCalls)
    try expectFalse(runbook.safety.globalMutation)
}

private func testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeployRunbookStatus: "partial",
            iosDeployRunbookSlotStatus: "missing",
            iosDeployRunbookAction: "set PMF_BACKEND_BASE_URL to the Mac LAN URL"
        ),
        error: nil
    )
    let runbookText = summary.deployRunbookRows.joined(separator: " ")
    let commandText = summary.deployRunbookCommandRows.joined(separator: " ")
    let safetyText = summary.deployRunbookSafetyRows.joined(separator: " ")

    try expectEqual(summary.deployRunbookRows.first, "iOS deploy runbook partial.")
    try expectContains(runbookText, "backend_base_url: missing required")
    try expectContains(runbookText, "set PMF_BACKEND_BASE_URL")
    try expectContains(commandText, "mobile_deploy_preflight: ready | make mobile-deploy-preflight")
    try expectContains(commandText, "mobile_xcode_build: blocked | make mobile-xcode-build")
    try expectContains(safetyText, "commands_run=false")
    try expectContains(safetyText, "provider_calls=false")
    try expectContains(safetyText, "global_mutation=false")
}

private func testFinalLaunchMobileSummaryShowsThreeDEvaluationIOSDeployRunbookSlot() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeployRunbookStatus: "blocked",
            iosDeployRunbookSlotStatus: "ready",
            iosDeployRunbookThreeDSlotStatus: "missing"
        ),
        error: nil
    )
    let text = summary.deployRunbookRows.joined(separator: " ")

    try expectEqual(summary.deployRunbookRows.first, "iOS deploy runbook blocked.")
    try expectContains(text, "three_d_evaluation: missing required")
    try expectContains(text, "run local 3D evaluation")
}

private func testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeployRunbookStatus: "blocked",
            iosDeployRunbookSlotStatus: "blocked",
            iosDeployRunbookAction: "provide DEVELOPMENT_TEAM and rerun mobile deploy preflight"
        ),
        error: nil
    )
    let text = summary.deployRunbookRows.joined(separator: " ")

    try expectEqual(summary.deployRunbookRows.first, "iOS deploy runbook blocked.")
    try expectContains(text, "backend_base_url: blocked required blocked_by_ios_deploy_config")
    try expectContains(text, "provide DEVELOPMENT_TEAM")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook() throws {
    let report = finalDemoLaunchReport(
        iosDeployRunbookStatus: "blocked",
        iosDeployRunbookSlotStatus: "blocked",
        iosDeployRunbookAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        iosDeployRunbookCommand: "make mobile-deploy-preflight sk-test /Users/zhexu/private file:///tmp/private"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDecodesIOSDeviceEvidenceBundleFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            iosDeviceEvidenceStatus: "blocked",
            iosDeviceEvidenceSlotStatus: "blocked"
        )
    )

    let bundle = try require(
        report.iosDeviceEvidenceBundle,
        "missing iOS device evidence bundle"
    )
    try expectEqual(bundle.kind, "ios_device_evidence_bundle_report")
    try expectEqual(bundle.status, "blocked")
    try expectEqual(bundle.summary.required, 4)
    try expectEqual(bundle.summary.globalActions, 1)
    try expectEqual(bundle.evidenceSlots[1].id, "mobile_deploy_preflight")
    try expectEqual(bundle.evidenceSlots[1].command, "make mobile-deploy-preflight")
    try expectEqual(bundle.evidenceSlots[2].globalAction, true)
    try expectEqual(bundle.evidenceSlots[2].xcodeOrSigning, true)
    try expectFalse(bundle.safety.commandsRun)
    try expectFalse(bundle.safety.xcodeOrSigning)
    try expectTrue(bundle.safety.describesGlobalActions)
}

private func testFinalLaunchMobileSummaryShowsIOSDeviceEvidenceBundle() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeviceEvidenceStatus: "blocked",
            iosDeviceEvidenceSlotStatus: "blocked",
            iosDeviceEvidenceAction: "run make mobile-deploy-preflight after backend is running"
        ),
        error: nil
    )
    let text = summary.deviceEvidenceRows.joined(separator: " ")

    try expectContains(text, "iOS device evidence blocked")
    try expectContains(text, "mobile_deploy_preflight")
    try expectContains(text, "make mobile-deploy-preflight")
    try expectContains(text, "commands_run=false xcode=false global=false")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceEvidenceBundle() throws {
    let report = finalDemoLaunchReport(
        iosDeviceEvidenceStatus: "blocked",
        iosDeviceEvidenceSlotStatus: "blocked",
        iosDeviceEvidenceAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        iosDeviceEvidenceDetail: "Authorization Bearer sk-test /Users/zhexu/private file:///tmp/private checkout_url"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
}

private func testDecodesIOSDeviceLaunchRehearsalReadinessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(iosDeviceLaunchRehearsalStatus: "blocked")
    )

    let readiness = try require(
        report.iosDeviceLaunchRehearsalReadiness,
        "missing iOS device launch rehearsal readiness"
    )
    try expectEqual(readiness.kind, "ios_device_launch_rehearsal_readiness_report")
    try expectEqual(readiness.status, "blocked")
    try expectEqual(readiness.sourceFile.path, "services/backend/.local/ios-device-launch-rehearsal.json")
    try expectEqual(readiness.summary.blocked, 1)
    try expectEqual(readiness.sequence.first?.id, "final_handoff_index")
    try expectEqual(readiness.sequence.first?.command, "make final-handoff-index")
    try expectEqual(
        readiness.sequence.first?.detail,
        "Final handoff index is stale; rerun safe refresh."
    )
    try expectFalse(readiness.safety.commandsRun)
    try expectFalse(readiness.safety.providerCalls)
}

private func testDecodesIOSDeviceLaunchRehearsalFreshnessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            iosDeviceLaunchRehearsalFreshnessClassification: "stale_report"
        )
    )

    let freshness = try require(
        report.iosDeviceLaunchRehearsalReadiness?.freshness,
        "missing iOS device launch rehearsal freshness"
    )
    try expectEqual(freshness.status, "fresh")
    try expectEqual(freshness.classification, "stale_report")
    try expectEqual(freshness.checkedAgainst, "git_head")
}

private func testDecodesIOSDeviceLaunchRehearsalSourceFreshnessFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchSourceFreshnessStatus: "stale",
            iosDeviceLaunchSourceFreshnessClassification: "stale_report",
            iosDeviceLaunchSourceFreshnessSummaryJSON: #"{"fresh": 4, "stale": 1, "unknown": 0}"#
        )
    )
    let row = try require(
        report.iosDeviceLaunchRehearsalReadiness?.sequence.first,
        "missing rehearsal sequence row"
    )

    try expectEqual(row.freshnessStatus, "stale")
    try expectEqual(row.freshnessClassification, "stale_report")
    try expectEqual(row.freshnessSummary?["stale"], 1)
}

private func testDecodesIOSDeviceLaunchCertificateFromFinalLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            iosDeviceLaunchCertificateStatus: "blocked",
            iosDeviceLaunchCertificateGateStatus: "blocked"
        )
    )

    let certificate = try require(
        report.iosDeviceLaunchCertificate,
        "missing iOS device launch certificate"
    )
    try expectEqual(certificate.kind, "ios_device_launch_certificate_report")
    try expectEqual(certificate.status, "blocked")
    try expectEqual(certificate.mode, "local")
    try expectEqual(certificate.summary.blocked, 1)
    try expectEqual(certificate.certificate.developmentTeam.key, "DEVELOPMENT_TEAM")
    try expectEqual(certificate.certificate.backendBaseURL.classification, "loopback_url")
    try expectEqual(certificate.deviceGates.first?.id, "final_handoff_index")
    try expectEqual(certificate.deviceGates.first?.command, "make final-handoff-index")
    try expectTrue(certificate.deviceGates.last?.requiresConsent ?? false)
    try expectEqual(certificate.operatorActions.first, "run make final-handoff-index")
    try expectFalse(certificate.safety.commandsRun)
    try expectFalse(certificate.safety.xcodeOrSigning)
}

private func testFinalLaunchMobileSummaryShowsBlockedIOSDeviceLaunchRehearsal() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalAction: "refresh final handoff index"
        ),
        error: nil
    )
    let text = summary.launchRehearsalRows.joined(separator: " ")

    try expectEqual(summary.launchRehearsalRows.first, "iOS launch rehearsal blocked: ready 3, blocked 1, partial 0.")
    try expectContains(text, "final_handoff_index: blocked")
    try expectContains(text, "make final-handoff-index")
    try expectContains(text, "Final handoff index is stale; rerun safe refresh.")
    try expectContains(text, "refresh final handoff index")
}

private func testFinalLaunchMobileSummaryShowsMultipleIOSDeviceLaunchRehearsalActions() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalActions: [
                "final_rehearsal_local: final_acceptance_local: provide iOS deploy config",
                "final_handoff_index: run make final-configured-preflight",
                "ios_device_launch_certificate: run make final-handoff-index",
            ]
        ),
        error: nil
    )
    let text = summary.launchRehearsalRows.joined(separator: " ")

    try expectContains(text, "final_rehearsal_local: final_acceptance_local")
    try expectContains(text, "final_handoff_index: run make final-configured-preflight")
    try expectContains(text, "ios_device_launch_certificate: run make final-handoff-index")
}

private func testFinalLaunchMobileSummaryShowsReadyIOSDeviceLaunchRehearsal() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(iosDeviceLaunchRehearsalStatus: "ready"),
        error: nil
    )

    try expectEqual(summary.launchRehearsalRows.first, "iOS launch rehearsal ready: ready 4, blocked 0, partial 0.")
    try expectContains(summary.launchRehearsalRows.joined(separator: " "), "Freshness: fresh_report")
    try expectContains(summary.launchRehearsalRows.joined(separator: " "), "safe evidence refreshed")
}

private func testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalFreshness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchRehearsalAction: "rerun make ios-device-launch-rehearsal",
            iosDeviceLaunchRehearsalFreshnessStatus: "stale",
            iosDeviceLaunchRehearsalFreshnessClassification: "stale_report"
        ),
        error: nil
    )
    let text = summary.launchRehearsalRows.joined(separator: " ")

    try expectContains(text, "Freshness: stale_report; rerun iOS device launch rehearsal.")
    try expectContains(text, "rerun make ios-device-launch-rehearsal")
}

private func testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalSourceFreshness() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            iosDeviceLaunchRehearsalStatus: "blocked",
            iosDeviceLaunchSourceFreshnessStatus: "stale",
            iosDeviceLaunchSourceFreshnessClassification: "stale_report",
            iosDeviceLaunchSourceFreshnessSummaryJSON: #"{"fresh": 4, "stale": 1, "unknown": 0}"#
        ),
        error: nil
    )
    let text = summary.launchRehearsalRows.joined(separator: " ")

    try expectContains(text, "Source freshness: 4 fresh, 1 stale, 0 unknown.")
    try expectContains(text, "stale_report")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceLaunchRehearsal() throws {
    let report = finalDemoLaunchReport(
        iosDeviceLaunchRehearsalStatus: "blocked",
        iosDeviceLaunchRehearsalAction: "rerun sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        iosDeviceLaunchRehearsalCommand: "make ios-device-launch-rehearsal sk-test /Users/zhexu/private file:///tmp/private",
        iosDeviceLaunchRehearsalDetail: "detail sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        iosDeviceLaunchRehearsalFreshnessClassification: "stale_report sk-test /Users/zhexu/private file:///tmp/private"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalLaunchMobileSummaryMarksReadyReport() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready"
        ),
        error: nil
    )

    try expectEqual(summary.overallStatus, .ready)
    try expectContains(summary.title, "Final launch ready")
    try expectEqual(summary.resourceActions.first, "Final resources file ready to apply.")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeReportText() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        unsafeDetail: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        finalResourcesStatus: "blocked",
        finalResourcesAction: "remove sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectEqual(summary.overallStatus, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeAcceptanceText() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        finalAcceptanceStatus: "blocked",
        finalAcceptanceBlockerDetail: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testFinalLaunchMobileSummaryRedactsUnsafeHandoffText() throws {
    let report = finalDemoLaunchReport(
        overallStatus: "blocked",
        finalOperatorHandoffStatus: "blocked",
        finalOperatorHandoffAction: "run sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDevicePreflightMarksLocalDemoReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalSummary = finalShowcaseSummary(session: session, npcTickHistoryCount: 3)
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        finalShowcaseSummary: finalSummary
    )

    try expectEqual(summary.item(id: "local_demo")?.status, .ready)
    try expectContains(summary.item(id: "local_demo")?.detail ?? "", "ready")
}

private func testDevicePreflightMarksSavedNPCHistoryReady() throws {
    let summary = devicePreflightSummary(
        backendBaseURL: URL(string: "http://192.168.1.10:8080")!,
        savedNPCTickCount: 2
    )

    try expectEqual(summary.item(id: "saved_history")?.status, .ready)
    try expectContains(summary.item(id: "saved_history")?.detail ?? "", "2")
}

private func testDemoScriptStartsWithCapture() throws {
    let script = DemoScriptBuilder.build(
        captureSelection: CaptureMediaSelection(mode: .singlePhoto),
        session: nil,
        npcTickHistoryCount: 0,
        printQuote: nil,
        providerReadiness: nil,
        providerReadinessError: nil
    )

    try expectEqual(script.title, "Live Demo Script")
    try expectEqual(script.nextAction, "Capture or import an object.")
    try expectEqual(
        script.steps.map(\.id),
        ["capture", "forge", "three_d_scene", "npc_autonomy", "print_quote", "resources"]
    )
    try expectEqual(script.step(id: "capture")?.status, .current)
    try expectEqual(script.step(id: "forge")?.status, .waiting)
    try expectEqual(script.step(id: "three_d_scene")?.status, .waiting)
}

private func testDemoScriptMovesToForgeWhenMediaReady() throws {
    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: nil,
        npcTickHistoryCount: 0,
        printQuote: nil,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(script.nextAction, "Forge the myth session.")
    try expectEqual(script.step(id: "capture")?.status, .complete)
    try expectEqual(script.step(id: "forge")?.status, .current)
    try expectEqual(script.step(id: "resources")?.status, .complete)
}

private func testDemoScriptMarksLocalDemoLoopReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(script.nextAction, "Local demo loop is ready.")
    try expectEqual(script.step(id: "capture")?.status, .complete)
    try expectEqual(script.step(id: "forge")?.status, .complete)
    try expectEqual(script.step(id: "three_d_scene")?.status, .complete)
    try expectContains(script.step(id: "three_d_scene")?.detail ?? "", "DAE")
    try expectEqual(script.step(id: "npc_autonomy")?.status, .complete)
    try expectContains(script.step(id: "npc_autonomy")?.detail ?? "", "3 ticks")
    try expectEqual(script.step(id: "print_quote")?.status, .complete)
    try expectEqual(script.step(id: "resources")?.status, .complete)
}

private func testDemoScriptBlocksOnProviderReadinessError() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 1,
        printQuote: nil,
        providerReadiness: nil,
        providerReadinessError: "Backend preflight is not reachable yet."
    )

    try expectEqual(script.step(id: "resources")?.status, .blocked)
    try expectContains(script.step(id: "resources")?.detail ?? "", "not reachable")
}

private func testDemoScriptRedactsUnsafeDetail() throws {
    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: nil,
        npcTickHistoryCount: 0,
        printQuote: nil,
        providerReadiness: nil,
        providerReadinessError: "sk-test /Users/zhexu/private file:///tmp/private checkout_url=https://pay.example"
    )
    let data = try PMFJSON.encoder.encode(script)
    let text = try require(String(data: data, encoding: .utf8), "expected encoded demo script text")

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "checkout")
}

private func testDemoScriptShowsBlockedFinalLaunch() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            finalAcceptanceStatus: "blocked",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready"
        ),
        error: nil
    )

    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(script.step(id: "final_launch")?.status, .blocked)
    try expectContains(script.step(id: "final_launch")?.detail ?? "", "blocked")
    try expectContains(script.nextAction, "final launch")
}

private func testDemoScriptFinalLaunchDetailUsesReceiptFirstBlocker() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "blocked",
            firstBlockerJSON: finalDemoLaunchTopLevelFirstBlockerJSON(),
            finalResourcesStatus: "blocked",
            finalAcceptanceStatus: "blocked",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready"
        ),
        error: nil
    )

    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let detail = script.step(id: "final_launch")?.detail ?? ""

    try expectEqual(script.step(id: "final_launch")?.status, .blocked)
    try expectContains(detail, "apply_final_resources")
    try expectContains(detail, "final_demo_launch_phase")
    try expectContains(detail, "make final-apply-resources")
}

private func testDemoScriptCompletesWithReadyFinalLaunch() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(script.step(id: "final_launch")?.status, .complete)
    try expectEqual(script.nextAction, "Final launch is ready.")
}

private func testDemoScriptRedactsUnsafeFinalLaunchDetail() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummary(
        overallStatus: .blocked,
        title: "Final launch blocked",
        subtitle: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token",
        phaseRows: [],
        resourceActions: [],
        acceptanceRows: [],
        threeDEvaluationRows: ["3D evaluation ready: 20 cases, 20 scene-loadable."],
        handoffRows: [],
        commandRows: [],
        notes: []
    )

    let script = DemoScriptBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        finalLaunchSummary: finalLaunch
    )
    let text = String(decoding: try PMFJSON.encoder.encode(script), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testDemoScriptShowsReadyThreeDEvaluationBeforeNPCEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )
    let threeDIndex = try require(script.steps.map(\.id).firstIndex(of: "three_d_evaluation"), "missing 3D evaluation step")
    let npcIndex = try require(script.steps.map(\.id).firstIndex(of: "npc_evaluation"), "missing npc evaluation step")

    try expectEqual(script.step(id: "three_d_evaluation")?.status, .complete)
    try expectContains(script.step(id: "three_d_evaluation")?.detail ?? "", "20 cases")
    try expectTrue(threeDIndex < npcIndex)
}

private func testDemoScriptWaitsForMissingThreeDEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "missing",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(script.step(id: "three_d_evaluation")?.status, .waiting)
    try expectContains(script.nextAction, "3D evaluation")
}

private func testDemoScriptBlocksAndRedactsFailedThreeDEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "blocked",
            threeDEvaluationBlockerDetail: "failed Authorization=Bearer test-secret private_message: raw",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )
    let detail = script.step(id: "three_d_evaluation")?.detail ?? ""

    try expectEqual(script.step(id: "three_d_evaluation")?.status, .blocked)
    try expectContains(detail, "[withheld]")
    try expectNotContains(detail, "test-secret")
    try expectNotContains(detail, "private_message:")
}

private func testDemoScriptShowsReadyNPCEvaluationBeforeFinalLaunch() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "ready",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )
    let npcIndex = try require(script.steps.map(\.id).firstIndex(of: "npc_evaluation"), "missing npc evaluation step")
    let launchIndex = try require(script.steps.map(\.id).firstIndex(of: "final_launch"), "missing final launch step")

    try expectEqual(script.step(id: "npc_evaluation")?.status, .complete)
    try expectContains(script.step(id: "npc_evaluation")?.detail ?? "", "6 cases")
    try expectTrue(npcIndex < launchIndex)
}

private func testDemoScriptWaitsForMissingNPCEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "missing",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )

    try expectEqual(script.step(id: "npc_evaluation")?.status, .waiting)
    try expectContains(script.nextAction, "NPC evaluation")
}

private func testDemoScriptBlocksAndRedactsFailedNPCEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let finalLaunch = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "ready",
            finalResourcesStatus: "ready",
            finalAcceptanceStatus: "ready",
            threeDEvaluationStatus: "ready",
            npcEvaluationStatus: "blocked",
            npcEvaluationBlockerDetail: "failed Authorization=Bearer test-secret private_message: raw",
            finalOperatorHandoffStatus: "ready"
        ),
        error: nil
    )

    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: localPrintQuote(),
        finalLaunchSummary: finalLaunch
    )
    let detail = script.step(id: "npc_evaluation")?.detail ?? ""

    try expectEqual(script.step(id: "npc_evaluation")?.status, .blocked)
    try expectContains(detail, "[withheld]")
    try expectNotContains(detail, "test-secret")
    try expectNotContains(detail, "private_message:")
}

private func testShowcaseAutopilotBlocksUntilCaptureReady() throws {
    let script = demoScript(captureSelection: CaptureMediaSelection(mode: .singlePhoto))

    let plan = autopilotPlan(script: script, session: nil)

    try expectEqual(plan.action, .blocked)
    try expectEqual(plan.buttonTitle, "Capture First")
    try expectFalse(plan.isExecutable)
    try expectContains(plan.detail, "Capture")
}

private func testShowcaseAutopilotPlansForgeWhenCaptureReady() throws {
    let script = demoScript(captureSelection: readyGuidedScanSelection())

    let plan = autopilotPlan(script: script, session: nil)

    try expectEqual(plan.action, .forge)
    try expectEqual(plan.buttonTitle, "Run Forge")
    try expectTrue(plan.isExecutable)
    try expectContains(plan.detail, "myth")
}

private func testShowcaseAutopilotPlansBackendAutonomyForReadySession() throws {
    let session = try backendHistorySession()
    let script = demoScript(session: session, npcTickHistoryCount: 1)

    let plan = autopilotPlan(script: script, session: session, npcTickHistoryCount: 1)

    try expectEqual(plan.action, .runAutonomy)
    try expectEqual(plan.buttonTitle, "Run NPCs")
    try expectTrue(plan.isExecutable)
    try expectContains(plan.detail, "3 ticks")
}

private func testShowcaseAutopilotPlansLegacyTickAdvanceForLegacySession() throws {
    var session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    session.sessionId = "legacy_session"
    let script = demoScript(session: session, npcTickHistoryCount: 1)

    let plan = autopilotPlan(script: script, session: session, npcTickHistoryCount: 1)

    try expectEqual(plan.action, .advanceNPC)
    try expectEqual(plan.buttonTitle, "Advance NPC")
    try expectTrue(plan.isExecutable)
    try expectContains(plan.detail, "legacy")
}

private func testShowcaseAutopilotPlansPrintQuoteAfterNPCAutonomy() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let script = demoScript(session: session, npcTickHistoryCount: 3)

    let plan = autopilotPlan(script: script, session: session, npcTickHistoryCount: 3)

    try expectEqual(plan.action, .requestQuote)
    try expectEqual(plan.buttonTitle, "Get Quote")
    try expectTrue(plan.isExecutable)
    try expectContains(plan.detail, "print")
}

private func testShowcaseAutopilotCompletesWhenQuoteAndResourcesReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(session: session, npcTickHistoryCount: 3, printQuote: quote)

    let plan = autopilotPlan(script: script, session: session, npcTickHistoryCount: 3, printQuote: quote)

    try expectEqual(plan.action, .complete)
    try expectEqual(plan.buttonTitle, "Ready")
    try expectFalse(plan.isExecutable)
    try expectContains(plan.detail, "ready")
}

private func testShowcaseAutopilotBlocksOnFinalLaunchBlocker() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "blocked",
                finalAcceptanceStatus: "blocked",
                threeDEvaluationStatus: "ready",
                npcEvaluationStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )

    try expectEqual(plan.action, .blocked)
    try expectEqual(plan.buttonTitle, "Check Launch")
    try expectFalse(plan.isExecutable)
    try expectContains(plan.detail, "final launch")
}

private func testShowcaseAutopilotCompletesWhenFinalLaunchReady() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "ready",
                finalResourcesStatus: "ready",
                finalAcceptanceStatus: "ready",
                threeDEvaluationStatus: "ready",
                npcEvaluationStatus: "ready",
                finalOperatorHandoffStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )

    try expectEqual(plan.action, .complete)
    try expectEqual(plan.buttonTitle, "Ready")
    try expectContains(plan.detail, "Final launch")
}

private func testShowcaseAutopilotWaitsForMissingThreeDEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "ready",
                finalResourcesStatus: "ready",
                finalAcceptanceStatus: "ready",
                threeDEvaluationStatus: "missing",
                npcEvaluationStatus: "ready",
                finalOperatorHandoffStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )

    try expectEqual(plan.action, .waiting)
    try expectEqual(plan.buttonTitle, "Check 3D Eval")
    try expectContains(plan.detail, "3D evaluation")
}

private func testShowcaseAutopilotBlocksOnFailedThreeDEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "ready",
                finalResourcesStatus: "ready",
                finalAcceptanceStatus: "ready",
                threeDEvaluationStatus: "blocked",
                threeDEvaluationBlockerDetail: "failed Authorization=Bearer test-secret private_message: raw",
                npcEvaluationStatus: "ready",
                finalOperatorHandoffStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )
    let text = String(decoding: try PMFJSON.encoder.encode(plan), as: UTF8.self)

    try expectEqual(plan.action, .blocked)
    try expectEqual(plan.buttonTitle, "Check 3D Eval")
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "test-secret")
    try expectNotContains(text, "private_message:")
}

private func testShowcaseAutopilotWaitsForMissingNPCEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "ready",
                finalResourcesStatus: "ready",
                finalAcceptanceStatus: "ready",
                threeDEvaluationStatus: "ready",
                npcEvaluationStatus: "missing",
                finalOperatorHandoffStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )

    try expectEqual(plan.action, .waiting)
    try expectEqual(plan.buttonTitle, "Check NPC Eval")
    try expectContains(plan.detail, "NPC evaluation")
}

private func testShowcaseAutopilotBlocksOnFailedNPCEvaluation() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        finalLaunchSummary: FinalLaunchMobileSummaryBuilder.build(
            report: finalDemoLaunchReport(
                overallStatus: "ready",
                finalResourcesStatus: "ready",
                finalAcceptanceStatus: "ready",
                threeDEvaluationStatus: "ready",
                npcEvaluationStatus: "blocked",
                finalOperatorHandoffStatus: "ready"
            ),
            error: nil
        )
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote
    )

    try expectEqual(plan.action, .blocked)
    try expectEqual(plan.buttonTitle, "Check NPC Eval")
}

private func testShowcaseAutopilotDisablesWhileBusy() throws {
    let script = demoScript(captureSelection: readyGuidedScanSelection())

    let forgePlan = autopilotPlan(script: script, phase: .creatingSession, session: nil)
    let autonomyPlan = autopilotPlan(
        script: script,
        phase: .idle,
        session: nil,
        isRunningAutonomy: true
    )
    let quotePlan = autopilotPlan(
        script: script,
        phase: .idle,
        session: nil,
        isLoadingPrintQuote: true
    )

    try expectEqual(forgePlan.action, .waiting)
    try expectEqual(autonomyPlan.action, .waiting)
    try expectEqual(quotePlan.action, .waiting)
    try expectFalse(forgePlan.isExecutable)
    try expectFalse(autonomyPlan.isExecutable)
    try expectFalse(quotePlan.isExecutable)
}

private func testShowcaseAutopilotRedactsUnsafeText() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let quote = localPrintQuote()
    let script = demoScript(
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        providerReadinessError: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )

    let plan = autopilotPlan(
        script: script,
        session: session,
        npcTickHistoryCount: 3,
        printQuote: quote,
        providerReadinessError: "sk-test /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url Bearer token"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(plan), as: UTF8.self)

    try expectEqual(plan.action, .blocked)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
}

private func testEncodesPrintQuoteRequestAsSnakeCase() throws {
    let request = PrintQuoteRequest(
        printCandidate: samplePrintCandidate(),
        quantity: 1,
        material: "standard_resin",
        finish: "matte",
        shipToCountry: "US"
    )

    let body = String(decoding: try PMFJSON.encoder.encode(request), as: UTF8.self)

    try expectContains(body, "\"print_candidate\":{")
    try expectContains(body, "\"source_asset_uri\":\"local:\\/\\/generated-assets\\/myth_test.glb\"")
    try expectContains(body, "\"ship_to_country\":\"US\"")
    try expectContains(body, "\"quantity\":1")
    try expectContains(body, "\"material\":\"standard_resin\"")
    try expectContains(body, "\"finish\":\"matte\"")
    try expectNotContains(body, "sourceAssetUri")
    try expectNotContains(body, "shipToCountry")
}

private func testCaptureIDValidation() throws {
    try expectTrue(CaptureID.isValid("cap_0123456789abcdef"))
    try expectFalse(CaptureID.isValid("cap_example"))
    try expectFalse(CaptureID.isValid(".."))
    try expectFalse(CaptureID.isValid("cap_0123456789abcdeg"))
}

private func testMythSessionIDValidation() throws {
    try expectTrue(MythSessionID.isValid("myth_0123456789abcdef"))
    try expectFalse(MythSessionID.isValid("myth_test"))
    try expectFalse(MythSessionID.isValid("../myth_0123456789abcdef"))
    try expectFalse(MythSessionID.isValid("myth_0123456789abcdeg"))
    try expectFalse(MythSessionID.isValid("session_cap_ba02a3816bd145b4"))
}

private func testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths() throws {
    var builder = MultipartFormDataBuilder(boundary: "pmf-boundary")
    let metadata = ObjectCaptureMetadata(
        label: "old brass key",
        materials: ["metal", "brass"],
        source: "phone_capture",
        captureMode: "single_photo",
        visualNotes: "worn teeth"
    )
    try builder.appendJSONField(name: "metadata_json", value: metadata)
    builder.appendFile(
        fieldName: "files",
        filename: "media_0.jpg",
        contentType: "image/jpeg",
        data: Data("fake-jpeg".utf8)
    )

    let body = String(decoding: builder.build(), as: UTF8.self)

    try expectContains(body, "name=\"metadata_json\"")
    try expectContains(body, "\"capture_mode\":\"single_photo\"")
    try expectContains(body, "filename=\"media_0.jpg\"")
    try expectContains(body, "Content-Type: image/jpeg")
    try expectNotContains(body, "/Users/")
}

private func testMultipartBuilderSanitizesHeaderValues() throws {
    var builder = MultipartFormDataBuilder(boundary: "pmf-boundary")
    builder.appendFile(
        fieldName: "files\r\nX-Injected: 1",
        filename: "../../secret.jpg\r\nX-Injected: 1",
        contentType: "image/jpeg\r\nX-Injected: 1",
        data: Data("fake-jpeg".utf8)
    )

    let body = String(decoding: builder.build(), as: UTF8.self)

    try expectContains(body, "name=\"files\"")
    try expectContains(body, "filename=\"secret.jpg\"")
    try expectContains(body, "Content-Type: application/octet-stream")
    try expectNotContains(body, "X-Injected")
    try expectNotContains(body, "../")
    try expectNotContains(body, "\r\nX-Injected")
}

private func testUploadObjectCaptureBuildsMultipartRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )

    let capture = try await client.uploadObjectCapture(
        metadata: sampleMetadata(),
        media: [
            CaptureUpload(
                filename: "media_0.jpg",
                contentType: "image/jpeg",
                data: Data("fake-jpeg".utf8)
            )
        ]
    )

    try expectEqual(capture.captureId, "cap_ba02a3816bd145b4")
    try expectEqual(transport.requests.count, 1)
    let request = try require(transport.requests.first, "missing upload request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/object-captures")
    try expectContains(request.value(forHTTPHeaderField: "Content-Type") ?? "", "multipart/form-data; boundary=test-boundary")
    try expectContains(String(decoding: request.httpBody ?? Data(), as: UTF8.self), "\"label\":\"old brass key\"")
}

private func testCreateMythSessionFromCaptureBuildsJSONRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "myth-session-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let session = try await client.createMythSessionFromCapture(
        captureId: "cap_ba02a3816bd145b4",
        context: sampleContext()
    )

    try expectEqual(session.status, "ready_for_review")
    let request = try require(transport.requests.first, "missing session request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/myth-sessions/from-capture")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    try expectContains(String(decoding: request.httpBody ?? Data(), as: UTF8.self), "\"capture_id\":\"cap_ba02a3816bd145b4\"")
}

private func testInvalidCaptureIDFailsBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(captureId: "..", context: sampleContext())
        throw ContractTestError.expectationFailed("Expected invalid capture id error")
    } catch ForgeFlowError.invalidCaptureID("..") {
        try expectEqual(transport.requests.count, 0)
    }
}

private func testHTTPStatusErrorIncludesStatusAndBody() async throws {
    let transport = RecordingTransport(
        responses: [
            HTTPResponse(statusCode: 500, data: Data("provider failed".utf8))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(
            captureId: "cap_ba02a3816bd145b4",
            context: sampleContext()
        )
        throw ContractTestError.expectationFailed("Expected HTTP status error")
    } catch ForgeFlowError.httpStatus(500, "provider failed") {
        try expectEqual(transport.requests.count, 1)
    }
}

private func testHTTPStatusErrorSanitizesSecretsAndTruncatesBody() async throws {
    let secret = "test-secret"
    let oversized = String(repeating: "x", count: 900)
    let body = "Authorization=Bearer \(secret) raw=\(secret) \(oversized)"
    let transport = RecordingTransport(
        responses: [
            HTTPResponse(statusCode: 502, data: Data(body.utf8))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(
            captureId: "cap_ba02a3816bd145b4",
            context: sampleContext()
        )
        throw ContractTestError.expectationFailed("Expected sanitized HTTP status error")
    } catch ForgeFlowError.httpStatus(502, let sanitizedBody) {
        try expectFalse(sanitizedBody.contains(secret))
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "raw=[redacted]")
        try expectContains(sanitizedBody, "[truncated]")
        try expectTrue(sanitizedBody.count <= 530)
    }
}

private func testGetBackendHealthBuildsGETRequest() async throws {
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 200, data: Data(#"{"status":"ok"}"#.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://192.168.1.10:8080")!,
        transport: transport
    )

    let health = try await client.getBackendHealth()

    try expectEqual(health.status, "ok")
    let request = try require(transport.requests.first, "missing backend health request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/health")
    try expectEqual(request.httpBody, nil)
}

private func testGetProviderReadinessBuildsGETRequest() async throws {
    let data = Data(
        """
        {
          "overall_demo_ready": true,
          "overall_real_ready": false,
          "providers": []
        }
        """.utf8
    )
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 200, data: data)]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let readiness = try await client.getProviderReadiness()

    try expectTrue(readiness.overallDemoReady)
    let request = try require(transport.requests.first, "missing readiness request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/provider-readiness")
    try expectEqual(request.httpBody, nil)
}

private func testGetProviderReadinessSanitizesHTTPErrorBody() async throws {
    let secret = "test-secret"
    let body = "Authorization=Bearer \(secret) api_key=\(secret)"
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 502, data: Data(body.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.getProviderReadiness()
        throw ContractTestError.expectationFailed("Expected sanitized readiness error")
    } catch ForgeFlowError.httpStatus(502, let sanitizedBody) {
        try expectFalse(sanitizedBody.contains(secret))
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "api_key=[redacted]")
    }
}

private func testDecodesFinalDemoLaunchPayload() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload()
    )

    try expectEqual(report.kind, "final_demo_launch_report")
    try expectEqual(report.mode, "local")
    try expectEqual(report.overallStatus, "partial")
    try expectEqual(report.summary.ready, 4)
    try expectEqual(report.phaseSummary?.blocked, 2)
    try expectEqual(report.launchPhases.map(\.id), ["backend_device_server", "final_launch"])
    try expectEqual(report.launchPhases[0].status, "ready")
    try expectEqual(report.launchPhases[0].command, "make backend-device-demo")
    try expectEqual(report.finalResourcesPreflight?.status, "missing")
    try expectEqual(
        report.finalResourcesPreflight?.resourcesFile.path,
        "services/backend/.local/final-resources.env"
    )
    try expectEqual(report.finalResourcesPreflight?.resourcesFile.exists, false)
    try expectEqual(report.finalResourcesPreflight?.summary.missing, 1)
    try expectEqual(report.operatorChecklist.first, "set PMF_BACKEND_BASE_URL to a LAN URL")
    try expectEqual(report.commands.first, "make backend-device-demo")
    try expectFalse(report.liveCallPolicy.liveCallsByDefault)
    try expectTrue(report.liveCallPolicy.configuredAcceptanceRequiresConsent)
    try expectEqual(report.liveCallPolicy.consentFlag, "--allow-live-provider-calls")
    try expectFalse(report.safety.providerSecretsInReport)
    try expectFalse(report.safety.localPathsInReport)
}

private func testDecodesConfiguredFinalDemoLaunchPayloadCommands() throws {
    let report = try PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(mode: "configured")
    )

    try expectEqual(report.mode, "configured")
    try expectTrue(report.commands.contains("make final-acceptance-configured"))
    let applyIndex = try require(
        report.commands.firstIndex(of: "make final-apply-resources"),
        "missing final apply command"
    )
    let configuredIndex = try require(
        report.commands.firstIndex(of: "make final-acceptance-configured"),
        "missing configured final acceptance command"
    )
    try expectTrue(applyIndex < configuredIndex)

    let summary = FinalLaunchMobileSummaryBuilder.build(report: report, error: nil)
    try expectEqual(summary.commandRows.first, "make final-acceptance-configured")
    try expectTrue(summary.commandRows.contains("make final-resource-requirements"))
}

private func testGetFinalDemoLaunchBuildsGETRequest() async throws {
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 200, data: finalDemoLaunchPayload())]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://192.168.1.10:8080")!,
        transport: transport
    )

    let report = try await client.getFinalDemoLaunch(mode: "local")

    try expectEqual(report.mode, "local")
    let request = try require(transport.requests.first, "missing final launch request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/final-demo-launch")
    try expectEqual(request.url?.query, "mode=local")
    try expectEqual(request.httpBody, nil)
}

private func testGetConfiguredFinalDemoLaunchBuildsGETRequest() async throws {
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 200, data: finalDemoLaunchPayload(mode: "configured"))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://192.168.1.10:8080")!,
        transport: transport
    )

    let report = try await client.getFinalDemoLaunch(mode: FinalLaunchMode.configured.rawValue)

    try expectEqual(report.mode, "configured")
    let request = try require(transport.requests.first, "missing final launch request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/final-demo-launch")
    try expectEqual(request.url?.query, "mode=configured")
}

private func testGetFinalDemoLaunchRejectsInvalidModeBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://192.168.1.10:8080")!,
        transport: transport
    )

    do {
        _ = try await client.getFinalDemoLaunch(mode: "live")
        throw ContractTestError.expectationFailed("Expected invalid final demo launch mode")
    } catch ForgeFlowError.encodingFailed(let message) {
        try expectContains(message, "Unsupported final demo launch mode")
        try expectEqual(transport.requests.count, 0)
    }
}

private func testFinalLaunchModeDefaultsToLocalForUnsafeValues() throws {
    try expectEqual(FinalLaunchMode.safe(rawValue: nil), .local)
    try expectEqual(FinalLaunchMode.safe(rawValue: ""), .local)
    try expectEqual(FinalLaunchMode.safe(rawValue: "live"), .local)
    try expectEqual(FinalLaunchMode.safe(rawValue: "configured"), .configured)
    try expectEqual(FinalLaunchMode.configured.displayLabel, "Configured")
}

private func testFinalLaunchMobileSummaryShowsLocalModePolicy() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(mode: "local"),
        error: nil
    )

    try expectEqual(summary.modePolicyRows.count, 3)
    try expectEqual(summary.modePolicyRows[0], "Mode: Local")
    try expectEqual(summary.modePolicyRows[1], "Live calls by default: no")
    try expectEqual(summary.modePolicyRows[2], "Consent flag: --allow-live-provider-calls")
}

private func testFinalLaunchMobileSummaryShowsConfiguredModePolicy() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(mode: "configured"),
        error: nil
    )

    try expectEqual(summary.modePolicyRows.count, 3)
    try expectEqual(summary.modePolicyRows[0], "Mode: Configured")
    try expectEqual(summary.modePolicyRows[1], "Live calls by default: no")
    try expectEqual(summary.modePolicyRows[2], "Consent flag: --allow-live-provider-calls")
}

private func testCreatePrintQuoteBuildsJSONRequest() async throws {
    let responseData = Data(
        """
        {
          "kind": "print_quote",
          "provider": "local_stub",
          "status": "draft_quote",
          "source_asset_uri": "local://generated-assets/myth_test.glb",
          "print_candidate_uri": "local://print-candidates/myth_test.3mf",
          "currency": "USD",
          "estimated_price_cents": 1600,
          "estimated_production_days": 5,
          "estimated_shipping_days": 6,
          "checkout_url": null,
          "requires_user_approval": true,
          "approval_reason": "Draft quote must be reviewed.",
          "quote_notes": ["local quote stub"]
        }
        """.utf8
    )
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: responseData)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let quote = try await client.createPrintQuote(
        printCandidate: samplePrintCandidate(),
        quantity: 1,
        material: "standard_resin",
        finish: "matte",
        shipToCountry: "US"
    )

    try expectEqual(quote.estimatedPriceCents, 1600)
    let request = try require(transport.requests.first, "missing print quote request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/print-quotes")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"print_candidate\":{")
    try expectContains(body, "\"uri\":\"local:\\/\\/print-candidates\\/myth_test.3mf\"")
    try expectContains(body, "\"ship_to_country\":\"US\"")
    try expectNotContains(body, "api_key")
    try expectNotContains(body, "checkout_url")
}

private func finalDemoLaunchTopLevelFirstBlockerJSON() -> String {
    """
    {
      "id": "apply_final_resources",
      "label": "Apply final resources",
      "status": "missing",
      "classification": "final_demo_launch_phase",
      "command": "make final-apply-resources",
      "detail": "one-file backend and iOS final demo handoff | Reads only ignored services/backend/.local/final-resources.env.",
      "source": "final_demo_launch_phase",
      "source_id": "apply_final_resources"
    }
    """
}

private func finalDemoLaunchTopLevelNextActionJSON() -> String {
    """
    {
      "id": "apply_final_resources",
      "label": "Apply final resources",
      "status": "missing",
      "classification": "final_demo_launch_phase",
      "command": "make final-apply-resources",
      "detail": "one-file backend and iOS final demo handoff | Reads only ignored services/backend/.local/final-resources.env.",
      "source": "first_blocker",
      "source_id": "apply_final_resources",
      "validation_command": "make final-demo-launch-local"
    }
    """
}

private func finalDemoLaunchPayload(
    mode: String = "local",
    includeStatus: Bool = true,
    status: String? = nil,
    overallStatus: String = "partial",
    firstBlockerJSON: String = "null",
    nextActionJSON: String = "null",
    unsafeDetail: String = "Launch report partial; review operator checklist.",
    commands: [String]? = nil,
    finalResourcesStatus: String = "missing",
    finalResourcesAction: String = "run make final-resource-init",
    finalResourcesItemsJSON: String = "[]",
    finalAcceptanceStatus: String = "missing",
    finalAcceptanceFreshnessStatus: String = "fresh",
    finalAcceptanceFreshnessClassification: String = "fresh_report",
    finalAcceptanceBlockerDetail: String = "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.",
    threeDEvaluationStatus: String = "missing",
    threeDEvaluationBlockerClassification: String = "three_d_evaluation_failed",
    threeDEvaluationBlockerDetail: String = "3D evaluation report contains failed cases.",
    visualRegressionStatus: String = "missing",
    visualRegressionFreshnessStatus: String = "fresh",
    visualRegressionFreshnessClassification: String = "fresh_report",
    visualRegressionBlockerClassification: String = "visual_regression_failed",
    visualRegressionBlockerDetail: String = "Visual regression report contains failed artifacts.",
    visualRegressionAction: String = "run make visual-regression-local",
    localShowcaseSmokeStatus: String = "succeeded",
    localShowcaseSmokeFailureDetail: String = "Local HTTP smoke completed.",
    liveProviderEvidenceStatus: String = "missing",
    liveProviderEvidenceBlockerDetail: String = "Missing provider handoff.",
    liveProviderEvidenceFirstID: String? = nil,
    liveProviderEvidenceFirstLabel: String? = nil,
    liveProviderEvidenceFirstStatus: String? = nil,
    liveProviderEvidenceFirstClassification: String? = nil,
    liveProviderEvidenceCommand: String? = nil,
    configuredEvidencePlanStatus: String = "blocked",
    configuredEvidencePlanBlockerDetail: String = "Configured 3D evidence requires MESHY_API_KEY and live provider consent.",
    configuredEvidenceBundleStatus: String = "blocked",
    configuredEvidenceBundleBlockerDetail: String = "Final resource fill guide is blocked before configured evidence bundle.",
    printFulfillmentReadinessStatus: String = "partial",
    printFulfillmentReadinessBlockerDetail: String = "Local print proof is ready; configured Treatstock quote evidence is not present.",
    printFulfillmentReadinessAction: String = "make print-fulfillment-readiness",
    finalResourceApplyPreviewStatus: String = "missing",
    finalShowcaseReadinessStatus: String = "partial",
    finalShowcaseReadinessFirstBlockerDetail: String = "iOS deploy runbook and device launch rehearsal must both be ready.",
    finalShowcaseReadinessAction: String = "make ios-device-launch-rehearsal",
    finalShowcaseReadinessActions: [String]? = nil,
    npcEvaluationStatus: String = "missing",
    npcEvaluationBlockerClassification: String = "npc_agent_evaluation_failed",
    npcEvaluationBlockerDetail: String = "NPC Agent evaluation report contains failed cases.",
    finalOperatorHandoffStatus: String = "missing",
    finalOperatorHandoffAction: String = "run make final-acceptance-local to write services/backend/.local/final-acceptance-local.json",
    iosDeployRunbookStatus: String = "partial",
    iosDeployRunbookSlotStatus: String = "ready",
    iosDeployRunbookThreeDSlotStatus: String = "ready",
    iosDeployRunbookAction: String = "set PMF_BACKEND_BASE_URL to the Mac LAN URL",
    iosDeployRunbookCommand: String = "make mobile-deploy-preflight",
    iosDeviceEvidenceStatus: String = "blocked",
    iosDeviceEvidenceSlotStatus: String = "missing",
    iosDeviceEvidenceAction: String = "run make mobile-deploy-preflight after backend is running",
    iosDeviceEvidenceDetail: String = "Run mobile deploy preflight after backend-device-demo is reachable.",
    iosDeviceEvidenceCommand: String = "make mobile-deploy-preflight",
    iosDeviceLaunchRehearsalStatus: String = "missing",
    iosDeviceLaunchRehearsalAction: String = "run make ios-device-launch-rehearsal",
    iosDeviceLaunchRehearsalActions: [String]? = nil,
    iosDeviceLaunchRehearsalCommand: String = "make final-handoff-index",
    iosDeviceLaunchRehearsalDetail: String = "Final handoff index is stale; rerun safe refresh.",
    iosDeviceLaunchRehearsalFreshnessStatus: String = "fresh",
    iosDeviceLaunchRehearsalFreshnessClassification: String = "fresh_report",
    iosDeviceLaunchRehearsalFreshnessSourceModifiedAt: String = "2026-06-07T12:05:00Z",
    iosDeviceLaunchRehearsalFreshnessCurrentRevision: String = "abc1234",
    iosDeviceLaunchSourceFreshnessStatus: String = "fresh",
    iosDeviceLaunchSourceFreshnessClassification: String = "fresh_report",
    iosDeviceLaunchSourceFreshnessSummaryJSON: String = #"{"fresh": 1, "stale": 0, "unknown": 0}"#,
    iosDeviceLaunchCertificateStatus: String = "blocked",
    iosDeviceLaunchCertificateGateStatus: String = "blocked",
    iosDeviceLaunchCertificateAction: String = "run make final-handoff-index",
    resourceHandoffStatus: String = "blocked",
    resourceHandoffBackendStatus: String = "missing",
    resourceHandoffIOSStatus: String = "blocked",
    resourceHandoffAction: String = "provide MESHY_API_KEY",
    resourceHandoffDestination: String = "services/backend/.env",
    externalActionLedgerCommand: String = "make final-external-action-ledger",
    externalActionLedgerDetail: String = "Inspect external action blockers.",
    closurePacketActionCommand: String = "make final-resource-fill-guide",
    closurePacketActionDetail: String = "Backend-only secret for live Meshy 3D generation.",
    closurePacketFirstBlockerCommand: String = "make final-resources-preflight",
    closurePacketFirstBlockerDetail: String = "Backend-only secret for live Meshy 3D generation.",
    closurePacketConfiguredBundleStatus: String = "blocked",
    closurePacketConfiguredBundleCommand: String = "make configured-live-evidence-bundle",
    closurePacketConfiguredBundleDetail: String = "Build configured live evidence bundle after resource and provider evidence are ready."
) -> Data {
    let liveEvidenceReady = liveProviderEvidenceStatus == "ready"
    let liveEvidenceBlocked = liveProviderEvidenceStatus == "blocked"
    let printReadinessReady = printFulfillmentReadinessStatus == "ready"
    let printReadinessBlocked = printFulfillmentReadinessStatus == "blocked"
    let iosDeviceLaunchActions = iosDeviceLaunchRehearsalActions ?? [
        iosDeviceLaunchRehearsalAction
    ]
    let iosDeviceLaunchActionsJSON = String(
        decoding: try! PMFJSON.encoder.encode(iosDeviceLaunchActions),
        as: UTF8.self
    )
    let iosDeviceLaunchCertificateReady = iosDeviceLaunchCertificateStatus == "ready"
    let iosDeviceLaunchCertificateGateEffectiveStatus = iosDeviceLaunchCertificateReady
        ? "ready"
        : iosDeviceLaunchCertificateGateStatus
    let iosDeviceLaunchCertificateActions = iosDeviceLaunchCertificateReady
        ? []
        : [iosDeviceLaunchCertificateAction]
    let iosDeviceLaunchCertificateActionsJSON = String(
        decoding: try! PMFJSON.encoder.encode(iosDeviceLaunchCertificateActions),
        as: UTF8.self
    )
    let iosDeviceEvidenceReady = iosDeviceEvidenceStatus == "ready"
    let iosDeviceEvidenceSummaryJSON = iosDeviceEvidenceReady
        ? #"{"ready": 4, "missing": 0, "blocked": 0, "manual": 0, "required": 4, "global_actions": 1}"#
        : #"{"ready": 0, "missing": 1, "blocked": 3, "manual": 0, "required": 4, "global_actions": 1}"#
    let finalShowcaseActions = finalShowcaseReadinessActions ?? [
        finalShowcaseReadinessAction
    ]
    let finalShowcaseActionsJSON = String(
        decoding: try! PMFJSON.encoder.encode(finalShowcaseActions),
        as: UTF8.self
    )
    let localSmokeSucceeded = localShowcaseSmokeStatus == "succeeded"
    let localSmokeSummaryJSON = localSmokeSucceeded
        ? #"{"passed": 10, "failed": 0, "http_steps": 6, "npc_ticks": 2, "downloads": 3}"#
        : #"{"passed": 0, "failed": 1, "http_steps": 1, "npc_ticks": 0, "downloads": 0}"#
    let localSmokeStepsJSON = localSmokeSucceeded ? """
    [
      {"id": "upload_guided_scan_capture", "status": "passed", "detail": "uploaded guided scan capture"},
      {"id": "create_session_from_capture", "status": "passed", "detail": "created local session"},
      {"id": "download_game_asset", "status": "passed", "detail": "downloaded GLB"},
      {"id": "download_scene_asset", "status": "passed", "detail": "downloaded DAE scene"},
      {"id": "run_npc_autonomy", "status": "passed", "detail": "ran NPC autonomy"},
      {"id": "create_print_quote", "status": "passed", "detail": "created print quote"},
      {"id": "download_print_asset", "status": "passed", "detail": "downloaded 3MF"},
      {"id": "history_contains_ticks", "status": "passed", "detail": "history includes ticks"},
      {"id": "generation_provenance", "status": "passed", "detail": "generation provenance recorded"},
      {"id": "report_safety", "status": "passed", "detail": "report is sanitized"}
    ]
    """ : """
    [
      {
        "id": "upload_guided_scan_capture",
        "status": "failed",
        "detail": "\(localShowcaseSmokeFailureDetail)"
      }
    ]
    """
    let defaultLiveEvidenceFirstID = liveEvidenceBlocked ? "three_d_evaluation_configured" : "provider_handoff"
    let defaultLiveEvidenceFirstLabel = liveEvidenceBlocked ? "Configured 3D evaluation" : "Provider handoff"
    let defaultLiveEvidenceFirstStatus = liveEvidenceReady ? "ready" : liveEvidenceBlocked ? "blocked" : "missing"
    let defaultLiveEvidenceFirstClassification = liveEvidenceReady ? "ready" : liveEvidenceBlocked ? "report_not_ready" : "missing_report"
    let defaultLiveEvidenceCommand = liveEvidenceBlocked
        ? "make backend-evaluate-3d-configured"
        : "make live-provider-evidence"
    let liveEvidenceFirstID = liveProviderEvidenceFirstID ?? defaultLiveEvidenceFirstID
    let liveEvidenceFirstLabel = liveProviderEvidenceFirstLabel ?? defaultLiveEvidenceFirstLabel
    let liveEvidenceFirstStatus = liveProviderEvidenceFirstStatus ?? defaultLiveEvidenceFirstStatus
    let liveEvidenceFirstClassification = liveProviderEvidenceFirstClassification ?? defaultLiveEvidenceFirstClassification
    let liveEvidenceCommand = liveProviderEvidenceCommand ?? defaultLiveEvidenceCommand
    let liveEvidenceFirstBlockerJSON = liveEvidenceReady ? "null" : """
    {
      "id": "\(liveEvidenceFirstID)",
      "label": "\(liveEvidenceFirstLabel)",
      "status": "\(liveEvidenceFirstStatus)",
      "classification": "\(liveEvidenceFirstClassification)",
      "command": "\(liveEvidenceCommand)",
      "detail": "\(liveProviderEvidenceBlockerDetail)",
      "requires_live_provider_consent": \(liveEvidenceBlocked ? "true" : "false")
    }
    """
    let liveEvidenceSummaryJSON = liveEvidenceReady
        ? #"{"ready": 5, "missing": 0, "blocked": 0, "partial": 0, "requires_live_provider_consent": 3}"#
        : liveEvidenceBlocked
            ? #"{"ready": 4, "missing": 0, "blocked": 1, "partial": 0, "requires_live_provider_consent": 3}"#
            : #"{"ready": 0, "missing": 5, "blocked": 0, "partial": 0, "requires_live_provider_consent": 3}"#
    let configuredEvidencePlanReady = configuredEvidencePlanStatus == "ready"
    let configuredEvidencePlanStepStatus = configuredEvidencePlanReady ? "ready" : "blocked"
    let configuredEvidencePlanSummaryJSON = configuredEvidencePlanReady
        ? #"{"steps": 6, "ready": 6, "ready_to_run": 0, "blocked": 0, "consent_required": 2, "planned_consent_steps": 3, "live_provider_steps": 2, "cost_steps": 2, "repo_local_write_steps": 2, "commands_run": 0}"#
        : #"{"steps": 6, "ready": 3, "ready_to_run": 1, "blocked": 2, "consent_required": 2, "planned_consent_steps": 3, "live_provider_steps": 2, "cost_steps": 2, "repo_local_write_steps": 2, "commands_run": 0}"#
    let configuredEvidencePlanOperatorActionsJSON = configuredEvidencePlanReady
        ? #"[]"#
        : #"["provide MESHY_API_KEY in services/backend/.env", "rerun configured 3D evidence after consent"]"#
    let configuredEvidenceBundleReady = configuredEvidenceBundleStatus == "ready"
    let configuredEvidenceBundleBlockerJSON = configuredEvidenceBundleReady ? "null" : """
    {
      "id": "final_resource_fill_guide",
      "label": "Final resource fill guide",
      "status": "blocked",
      "command": "make final-resource-fill-guide",
      "detail": "\(configuredEvidenceBundleBlockerDetail)",
      "blocked_by": ["MESHY_API_KEY"]
    }
    """
    let configuredEvidenceBundleSummaryJSON = configuredEvidenceBundleReady
        ? #"{"evidence_files": 5, "evidence_ready": 5, "evidence_missing": 0, "evidence_blocked": 0, "evidence_partial": 0, "commands": 6, "commands_ready": 6, "commands_ready_to_run": 0, "blocked_steps": 0, "consent_required_steps": 0, "live_provider_steps": 3, "cost_steps": 3, "repo_local_write_steps": 1, "commands_run": 0}"#
        : #"{"evidence_files": 5, "evidence_ready": 0, "evidence_missing": 5, "evidence_blocked": 0, "evidence_partial": 0, "commands": 6, "commands_ready": 3, "commands_ready_to_run": 0, "blocked_steps": 2, "consent_required_steps": 1, "live_provider_steps": 3, "cost_steps": 3, "repo_local_write_steps": 1, "commands_run": 0}"#
    let configuredEvidenceBundleOperatorActionsJSON = configuredEvidenceBundleReady
        ? #"[]"#
        : #"["unblock final_resource_fill_guide before configured evidence bundle", "make configured-live-evidence-bundle"]"#
    let printReadinessFirstStatus = printReadinessReady ? "ready" : printReadinessBlocked ? "blocked" : "partial"
    let printReadinessFirstClassification = printReadinessReady
        ? "draft_quote_requires_user_approval"
        : printReadinessBlocked ? "missing_user_approval_gate" : "missing_configured_treatstock_quote"
    let printReadinessFirstBlockerJSON = printReadinessReady ? "null" : """
    {
      "id": "configured_treatstock_quote",
      "label": "Configured Treatstock quote",
      "status": "\(printReadinessFirstStatus)",
      "classification": "\(printReadinessFirstClassification)",
      "command": "make print-fulfillment-readiness",
      "detail": "\(printFulfillmentReadinessBlockerDetail)"
    }
    """
    let printReadinessSummaryJSON = printReadinessReady
        ? #"{"ready": 5, "partial": 0, "blocked": 0}"#
        : printReadinessBlocked
            ? #"{"ready": 4, "partial": 0, "blocked": 1}"#
            : #"{"ready": 4, "partial": 1, "blocked": 0}"#
    let selectedCommands = commands ?? defaultFinalDemoLaunchCommands(mode: mode)
    let commandsJSON = String(
        decoding: try! PMFJSON.encoder.encode(selectedCommands),
        as: UTF8.self
    )
    let statusLine = includeStatus
        ? #""status": "\#(status ?? overallStatus)","#
        : ""
    return Data(
        """
        {
          "kind": "final_demo_launch_report",
          "mode": "\(mode)",
          \(statusLine)
          "overall_status": "\(overallStatus)",
          "first_blocker": \(firstBlockerJSON),
          "next_action": \(nextActionJSON),
          "summary": {
            "ready": 4,
            "missing": 3,
            "blocked": 1,
            "manual": 3,
            "optional": 2,
            "partial": 0
          },
          "phase_summary": {
            "ready": 3,
            "missing": 0,
            "blocked": 2,
            "manual": 1,
            "optional": 2,
            "partial": 0
          },
          "final_resources_preflight": {
            "kind": "final_resources_preflight_report",
            "status": "\(finalResourcesStatus)",
            "resources_file": {
              "path": "services/backend/.local/final-resources.env",
              "exists": \(finalResourcesStatus == "missing" ? "false" : "true")
            },
            "summary": {
              "ready": \(finalResourcesStatus == "ready" ? "5" : "0"),
              "missing": \(finalResourcesStatus == "missing" ? "1" : "0"),
              "blocked": \(finalResourcesStatus == "blocked" ? "1" : "0"),
              "optional": 2
            },
            "items": \(finalResourcesItemsJSON),
            "unknown_keys": [],
            "malformed_lines": [],
            "operator_actions": ["\(finalResourcesAction)"],
            "safety": {
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "live_provider_calls": false,
              "global_mutation": false
            }
          },
          "final_resource_requirements": {
            "kind": "final_resource_requirements_report",
            "status": "blocked",
            "summary": {
              "total": 13,
              "ready": 0,
              "missing": 5,
              "blocked": 1,
              "optional": 7,
              "required": 5,
              "secret": 4,
              "backend": 10,
              "ios": 4,
              "print": 4,
              "validation_commands": 4
            },
            "first_blocker": {
              "id": "MESHY_API_KEY",
              "label": "Meshy API key",
              "status": "missing",
              "classification": "missing_required_value",
              "command": "provide MESHY_API_KEY in final-resources.env",
              "detail": "Backend-only secret for live Meshy 3D generation.",
              "domain": "backend_provider",
              "destination": "services/backend/.local/final-resources.env",
              "validation_command": "make final-resources-preflight"
            },
            "next_action": {
              "id": "MESHY_API_KEY",
              "label": "Meshy API key",
              "status": "missing",
              "classification": "missing_required_value",
              "command": "provide MESHY_API_KEY in final-resources.env",
              "detail": "Backend-only secret for live Meshy 3D generation.",
              "domain": "backend_provider",
              "destination": "services/backend/.local/final-resources.env",
              "validation_command": "make final-resources-preflight",
              "source": "first_blocker"
            },
            "requirements": [
              {
                "id": "MESHY_API_KEY",
                "label": "Meshy API key",
                "domain": "backend_provider",
                "destination": "services/backend/.local/final-resources.env",
                "source_template": "services/backend/final-resources.env.example",
                "required": true,
                "secret": true,
                "configured": false,
                "status": "missing",
                "classification": "missing_required_value",
                "unblocks": ["game_asset_3d_generation", "provider_key_handoff"],
                "validation_command": "make final-resources-preflight",
                "notes": "Backend-only secret for live Meshy 3D generation."
              },
              {
                "id": "PMF_BACKEND_BASE_URL",
                "label": "iPhone backend URL",
                "domain": "ios_deploy",
                "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "source_template": "apps/mobile/ios/Config/Deployment.local.xcconfig.example",
                "required": true,
                "secret": false,
                "configured": false,
                "status": "blocked",
                "classification": "loopback_url",
                "unblocks": ["ios_deployable", "capture_scanning"],
                "validation_command": "make final-resources-preflight",
                "notes": "Must be an iPhone-reachable LAN URL."
              }
            ],
            "requirements_by_id": {
              "MESHY_API_KEY": {
                "id": "MESHY_API_KEY",
                "label": "Meshy API key",
                "domain": "backend_provider",
                "destination": "services/backend/.local/final-resources.env",
                "source_template": "services/backend/final-resources.env.example",
                "required": true,
                "secret": true,
                "configured": false,
                "status": "missing",
                "classification": "missing_required_value",
                "unblocks": ["game_asset_3d_generation", "provider_key_handoff"],
                "validation_command": "make final-resources-preflight",
                "notes": "Backend-only secret for live Meshy 3D generation."
              },
              "PMF_BACKEND_BASE_URL": {
                "id": "PMF_BACKEND_BASE_URL",
                "label": "iPhone backend URL",
                "domain": "ios_deploy",
                "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "source_template": "apps/mobile/ios/Config/Deployment.local.xcconfig.example",
                "required": true,
                "secret": false,
                "configured": false,
                "status": "blocked",
                "classification": "loopback_url",
                "unblocks": ["ios_deployable", "capture_scanning"],
                "validation_command": "make final-resources-preflight",
                "notes": "Must be an iPhone-reachable LAN URL."
              }
            },
            "operator_actions": [
              "provide MESHY_API_KEY in final-resources.env",
              "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
            ],
            "validation_commands": [
              "make final-resource-requirements",
              "make final-resources-preflight"
            ],
            "source_reports": {
              "final_resources_preflight": {
                "kind": "final_resources_preflight_report",
                "status": "\(finalResourcesStatus)",
                "summary": {
                  "ready": 0,
                  "missing": 1,
                  "blocked": 0,
                  "optional": 0
                },
                "resources_file": {
                  "path": "services/backend/.local/final-resources.env",
                  "exists": \(finalResourcesStatus == "missing" ? "false" : "true")
                }
              }
            },
            "resources_file": {
              "path": "services/backend/.local/final-resources.env",
              "exists": \(finalResourcesStatus == "missing" ? "false" : "true")
            },
            "safety": {
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "live_provider_calls": false,
              "global_mutation": false
            }
          },
          "final_resource_fill_guide": {
            "kind": "final_resource_fill_guide_report",
            "status": "blocked",
            "summary": {
              "required_inputs": 5,
              "optional_inputs": 5,
              "configured_inputs": 3,
              "secret_inputs": 4
            },
            "first_blocker": {
              "id": "MESHY_API_KEY",
              "label": "Meshy API key",
              "status": "missing",
              "classification": "missing_required_value",
              "command": "fill MESHY_API_KEY in services/backend/.local/final-resources.env",
              "detail": "Backend-only secret for live Meshy 3D generation.",
              "domain": "backend_provider",
              "input_source": "services/backend/.local/final-resources.env",
              "write_destination": "services/backend/.env",
              "validation_command": "make final-resources-preflight"
            },
            "required_inputs": [
              {
                "id": "MESHY_API_KEY",
                "label": "Meshy API key",
                "domain": "backend_provider",
                "status": "missing",
                "classification": "missing_required_value",
                "required": true,
                "secret": true,
                "display_value": "<secret: fill locally>",
                "input_source": "services/backend/.local/final-resources.env",
                "write_destination": "services/backend/.env",
                "apply_command": "make final-apply-resources",
                "validation_command": "make final-resources-preflight",
                "fill_action": "fill MESHY_API_KEY in services/backend/.local/final-resources.env",
                "notes": "Backend-only secret for live Meshy 3D generation.",
                "unblocks": ["game_asset_3d_generation", "provider_key_handoff"]
              },
              {
                "id": "OPENAI_API_KEY",
                "label": "OpenAI API key",
                "domain": "backend_provider",
                "status": "missing",
                "classification": "missing_required_value",
                "required": true,
                "secret": true,
                "display_value": "<secret: fill locally>",
                "input_source": "services/backend/.local/final-resources.env",
                "write_destination": "services/backend/.env",
                "apply_command": "make final-apply-resources",
                "validation_command": "make final-resources-preflight",
                "fill_action": "fill OPENAI_API_KEY in services/backend/.local/final-resources.env",
                "notes": "Backend-only secret for live AI NPC Agent behavior.",
                "unblocks": ["ai_agent_npc", "provider_key_handoff"]
              }
            ],
            "optional_inputs": [
              {
                "id": "PRINT_PROVIDER",
                "label": "Print provider",
                "domain": "print_provider",
                "status": "optional",
                "classification": "optional_value_not_required",
                "required": false,
                "secret": false,
                "display_value": "<fill locally>",
                "input_source": "services/backend/.local/final-resources.env",
                "write_destination": "services/backend/.env",
                "apply_command": "make final-apply-resources",
                "validation_command": "make print-fulfillment-readiness",
                "fill_action": "fill PRINT_PROVIDER in services/backend/.local/final-resources.env",
                "notes": "Use local for demo quote stubs or treatstock for configured quote checks.",
                "unblocks": ["print_fulfillment"]
              }
            ],
            "configured_inputs": [
              {
                "id": "PMF_FINAL_LAUNCH_MODE",
                "label": "Final launch mode",
                "domain": "final_launch",
                "status": "ready",
                "classification": "configured",
                "required": false,
                "secret": false,
                "display_value": "<fill locally>",
                "input_source": "services/backend/.local/final-resources.env",
                "write_destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "apply_command": "make final-apply-resources",
                "validation_command": "make final-configured-preflight",
                "fill_action": "fill PMF_FINAL_LAUNCH_MODE in services/backend/.local/final-resources.env",
                "notes": "Optional local/configured switch for the iPhone launch panel.",
                "unblocks": ["provider_key_handoff", "privacy_safety"]
              }
            ],
            "commands": [
              "make final-resource-requirements",
              "make final-resource-apply-preview",
              "make final-apply-resources",
              "make final-local-report-refresh"
            ],
            "markdown": "# Final Resource Fill Guide",
            "source_reports": {
              "final_resource_requirements": {
                "kind": "final_resource_requirements_report",
                "status": "blocked",
                "summary": {
                  "total": 13,
                  "missing": 5,
                  "blocked": 1
                }
              }
            },
            "safety": {
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "writes_final_resources": false,
              "live_provider_calls": false,
              "global_mutation": false
            }
          },
          "final_resource_apply_preview": {
            "kind": "final_resource_apply_preview_report",
            "status": "\(finalResourceApplyPreviewStatus)",
            "summary": {
              "ready": \(finalResourceApplyPreviewStatus == "ready" ? "8" : "0"),
              "missing": \(finalResourceApplyPreviewStatus == "ready" ? "0" : "5"),
              "blocked": 0,
              "optional": 8,
              "secret": 4,
              "backend": 9,
              "ios": 4,
              "print": 4,
              "write_targets": 2
            },
            "resources_file": {
              "path": "services/backend/.local/final-resources.env",
              "exists": \(finalResourcesStatus == "missing" ? "false" : "true")
            },
            "first_blocker": {
              "id": "backend_env",
              "label": "Backend env",
              "status": "missing",
              "classification": "missing_required_value",
              "command": "make final-apply-resources",
              "detail": "blocked by MESHY_API_KEY",
              "destination": "services/backend/.env",
              "writer": "services/backend/scripts/write_backend_env.sh",
              "blocked_by": ["MESHY_API_KEY"],
              "validation_command": "make final-resources-preflight"
            },
            "write_targets": [
              {
                "id": "backend_env",
                "label": "Backend env",
                "destination": "services/backend/.env",
                "writer": "services/backend/scripts/write_backend_env.sh",
                "status": "missing",
                "command": "make final-apply-resources",
                "slots": [
                  {
                    "id": "MESHY_API_KEY",
                    "status": "missing",
                    "required": true,
                    "secret": true,
                    "configured": false,
                    "classification": "missing_required_value",
                    "redacted": true,
                    "writes": ["MESHY_API_KEY"]
                  }
                ],
                "blocked_by": ["MESHY_API_KEY"],
                "notes": ["Preview does not write services/backend/.env."]
              },
              {
                "id": "ios_deploy_config",
                "label": "iOS deploy config",
                "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "writer": "apps/mobile/ios/scripts/write_deploy_local_config.sh",
                "status": "missing",
                "command": "make final-apply-resources",
                "slots": [
                  {
                    "id": "PMF_BACKEND_BASE_URL",
                    "status": "missing",
                    "required": true,
                    "secret": false,
                    "configured": false,
                    "classification": "missing_required_value",
                    "redacted": false,
                    "writes": ["PMF_BACKEND_BASE_URL"]
                  }
                ],
                "blocked_by": ["PMF_BACKEND_BASE_URL"],
                "notes": ["Preview does not write Deployment.local.xcconfig."]
              }
            ],
            "write_targets_by_id": {
              "backend_env": {
                "id": "backend_env",
                "label": "Backend env",
                "destination": "services/backend/.env",
                "writer": "services/backend/scripts/write_backend_env.sh",
                "status": "missing",
                "command": "make final-apply-resources",
                "slots": [
                  {
                    "id": "MESHY_API_KEY",
                    "status": "missing",
                    "required": true,
                    "secret": true,
                    "configured": false,
                    "classification": "missing_required_value",
                    "redacted": true,
                    "writes": ["MESHY_API_KEY"]
                  }
                ],
                "blocked_by": ["MESHY_API_KEY"],
                "notes": ["Preview does not write services/backend/.env."]
              },
              "ios_deploy_config": {
                "id": "ios_deploy_config",
                "label": "iOS deploy config",
                "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "writer": "apps/mobile/ios/scripts/write_deploy_local_config.sh",
                "status": "missing",
                "command": "make final-apply-resources",
                "slots": [
                  {
                    "id": "PMF_BACKEND_BASE_URL",
                    "status": "missing",
                    "required": true,
                    "secret": false,
                    "configured": false,
                    "classification": "missing_required_value",
                    "redacted": false,
                    "writes": ["PMF_BACKEND_BASE_URL"]
                  }
                ],
                "blocked_by": ["PMF_BACKEND_BASE_URL"],
                "notes": ["Preview does not write Deployment.local.xcconfig."]
              }
            },
            "operator_actions": [
              "run make final-resource-init"
            ],
            "commands": [
              "make final-resource-apply-preview",
              "make final-resources-preflight",
              "make final-apply-resources"
            ],
            "source_reports": {
              "final_resources_preflight": {
                "kind": "final_resources_preflight_report",
                "status": "\(finalResourcesStatus)",
                "summary": {
                  "ready": 0,
                  "missing": 1,
                  "blocked": 0,
                  "optional": 0
                }
              },
              "final_resource_requirements": {
                "kind": "final_resource_requirements_report",
                "status": "blocked",
                "summary": {
                  "ready": 0,
                  "missing": 5,
                  "blocked": 0
                }
              }
            },
            "safety": {
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "runs_shell_writers": false,
              "live_provider_calls": false,
              "global_mutation": false,
              "xcode_or_signing": false
            }
          },
          "final_external_action_ledger": {
            "kind": "final_external_action_ledger_report",
            "status": "blocked",
            "summary": {
              "groups": 5,
              "actions": 27,
              "ready": 0,
              "missing": 6,
              "blocked": 4,
              "manual": 5,
              "live": 5,
              "partial": 0,
              "optional": 8,
              "secret": 4,
              "requires_user_confirmation": 3,
              "requires_cost_consent": 5,
              "global": 3,
              "safe_local_write": 2,
              "live_provider_call": 5
            },
            "action_groups": [
              {
                "id": "resource_inputs",
                "label": "Resource inputs",
                "status": "blocked",
                "summary": {
                  "actions": 13,
                  "ready": 0,
                  "missing": 5,
                  "blocked": 1,
                  "manual": 0,
                  "live": 0,
                  "partial": 0,
                  "optional": 7,
                  "secret": 4,
                  "requires_user_confirmation": 0,
                  "requires_cost_consent": 0
                },
                "actions": [
                  {
                    "id": "provide_MESHY_API_KEY",
                    "group_id": "resource_inputs",
                    "label": "Meshy API key",
                    "status": "missing",
                    "command": "make final-resources-preflight",
                    "detail": "Backend-only secret for live Meshy 3D generation.",
                    "required": true,
                    "secret": true,
                    "requires_user_input": true,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ]
              },
              {
                "id": "live_provider_costs",
                "label": "Live provider costs",
                "status": "live",
                "summary": {
                  "actions": 5,
                  "ready": 0,
                  "missing": 0,
                  "blocked": 0,
                  "manual": 0,
                  "live": 5,
                  "partial": 0,
                  "optional": 0,
                  "secret": 0,
                  "requires_user_confirmation": 0,
                  "requires_cost_consent": 5
                },
                "actions": [
                  {
                    "id": "run_live_provider_evidence",
                    "group_id": "live_provider_costs",
                    "label": "Refresh live provider evidence",
                    "status": "live",
                    "command": "\(externalActionLedgerCommand)",
                    "detail": "\(externalActionLedgerDetail)",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": true,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": true,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ]
              },
              {
                "id": "global_machine_actions",
                "label": "Global machine actions",
                "status": "manual",
                "summary": {
                  "actions": 3,
                  "ready": 0,
                  "missing": 0,
                  "blocked": 0,
                  "manual": 3,
                  "live": 0,
                  "partial": 0,
                  "optional": 0,
                  "secret": 0,
                  "requires_user_confirmation": 3,
                  "requires_cost_consent": 0
                },
                "actions": [
                  {
                    "id": "run_xcode_build_gate",
                    "group_id": "global_machine_actions",
                    "label": "Run Xcode build gate",
                    "status": "manual",
                    "command": "make mobile-xcode-build",
                    "detail": "May invoke Xcode signing and Apple SDK global state.",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": true,
                    "requires_cost_consent": false,
                    "global": true,
                    "xcode_or_signing": true,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ]
              }
            ],
            "actions_by_id": {
              "provide_MESHY_API_KEY": {
                "id": "provide_MESHY_API_KEY",
                "group_id": "resource_inputs",
                "label": "Meshy API key",
                "status": "missing",
                "command": "make final-resources-preflight",
                "detail": "Backend-only secret for live Meshy 3D generation.",
                "required": true,
                "secret": true,
                "requires_user_input": true,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false,
                "writes_repo_local_files": false
              },
              "run_xcode_build_gate": {
                "id": "run_xcode_build_gate",
                "group_id": "global_machine_actions",
                "label": "Run Xcode build gate",
                "status": "manual",
                "command": "make mobile-xcode-build",
                "detail": "May invoke Xcode signing and Apple SDK global state.",
                "required": true,
                "secret": false,
                "requires_user_input": false,
                "requires_user_confirmation": true,
                "requires_cost_consent": false,
                "global": true,
                "xcode_or_signing": true,
                "live_provider_call": false,
                "safe_local_write": false,
                "writes_repo_local_files": false
              }
            },
            "operator_sequence": [
              "make final-resource-requirements",
              "\(externalActionLedgerCommand)"
            ],
            "operator_actions": [
              "\(externalActionLedgerDetail)"
            ],
            "safety": {
              "commands_run": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "runs_shell_writers": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "requires_user_confirmation_for_global_actions": true,
              "requires_cost_consent_for_live_actions": true
            }
          },
          "final_launch_closure_packet": {
            "kind": "final_launch_closure_packet_report",
            "status": "blocked",
            "first_blocker": {
              "id": "resource_inputs",
              "label": "Resource inputs",
              "status": "blocked",
              "classification": "missing_required_value",
              "command": "\(closurePacketFirstBlockerCommand)",
              "detail": "\(closurePacketFirstBlockerDetail)",
              "section_id": "resource_inputs",
              "action_id": "provide_MESHY_API_KEY"
            },
            "summary": {
              "sections": 6,
              "actions": 8,
              "ready": 0,
              "missing": 0,
              "blocked": 4,
              "manual": 0,
              "live": 1,
              "partial": 1,
              "optional": 0,
              "required_sections": 5,
              "required_actions": 8,
              "secret_actions": 2,
              "requires_user_input": 2,
              "requires_user_confirmation": 1,
              "requires_cost_consent": 5,
              "global_actions": 1,
              "xcode_or_signing_actions": 1,
              "safe_local_writes": 2,
              "live_provider_calls": 5
            },
            "sections": [
              {
                "id": "resource_inputs",
                "label": "Resource inputs",
                "status": "blocked",
                "command": "make final-resource-fill-guide",
                "detail": "Fill required final resource inputs.",
                "required": true,
                "actions": [
                  {
                    "id": "provide_MESHY_API_KEY",
                    "label": "Meshy API key",
                    "status": "missing",
                    "command": "\(closurePacketActionCommand)",
                    "detail": "\(closurePacketActionDetail)",
                    "required": true,
                    "secret": true,
                    "requires_user_input": true,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ],
                "first_action": {
                  "id": "provide_MESHY_API_KEY",
                  "label": "Meshy API key",
                  "status": "missing",
                  "command": "\(closurePacketActionCommand)",
                  "detail": "\(closurePacketActionDetail)",
                  "required": true,
                  "secret": true,
                  "requires_user_input": true,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["provide_MESHY_API_KEY"],
                "requires_user_input": true,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              },
              {
                "id": "safe_local_writes",
                "label": "Safe local writes",
                "status": "blocked",
                "command": "make final-resource-apply-preview",
                "detail": "Preview and apply ignored backend/iOS local resource files.",
                "required": true,
                "actions": [
                  {
                    "id": "apply_final_resources",
                    "label": "Apply final resources",
                    "status": "blocked",
                    "command": "make final-apply-resources",
                    "detail": "Write ignored backend and iOS local config files after preview is ready.",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": true,
                    "writes_repo_local_files": true
                  }
                ],
                "first_action": {
                  "id": "apply_final_resources",
                  "label": "Apply final resources",
                  "status": "blocked",
                  "command": "make final-apply-resources",
                  "detail": "Write ignored backend and iOS local config files after preview is ready.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": true,
                  "writes_repo_local_files": true
                },
                "blocked_by": ["apply_final_resources"],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": true
              },
              {
                "id": "device_evidence",
                "label": "Device evidence",
                "status": "blocked",
                "command": "make ios-device-launch-rehearsal",
                "detail": "Collect backend LAN, deploy preflight, Xcode, and rehearsal proof.",
                "required": true,
                "actions": [
                  {
                    "id": "mobile_deploy_preflight",
                    "label": "Mobile deploy preflight",
                    "status": "blocked",
                    "command": "make mobile-deploy-preflight",
                    "detail": "Run mobile deploy preflight after backend-device-demo is reachable.",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ],
                "first_action": {
                  "id": "mobile_deploy_preflight",
                  "label": "Mobile deploy preflight",
                  "status": "blocked",
                  "command": "make mobile-deploy-preflight",
                  "detail": "Run mobile deploy preflight after backend-device-demo is reachable.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["mobile_deploy_preflight"],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              },
              {
                "id": "live_provider_consent",
                "label": "Live provider consent",
                "status": "live",
                "command": "make live-provider-evidence",
                "detail": "Run Meshy, OpenAI, and print-provider evidence only after cost consent.",
                "required": false,
                "actions": [
                  {
                    "id": "run_live_provider_evidence",
                    "label": "Refresh live provider evidence",
                    "status": "live",
                    "command": "make live-provider-evidence",
                    "detail": "Refresh configured Meshy/OpenAI evidence after cost consent.",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": true,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": true,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ],
                "first_action": {
                  "id": "run_live_provider_evidence",
                  "label": "Refresh live provider evidence",
                  "status": "live",
                  "command": "make live-provider-evidence",
                  "detail": "Refresh configured Meshy/OpenAI evidence after cost consent.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": true,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": true,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": [],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": true,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": true,
                "safe_local_write": false
              },
              {
                "id": "configured_evidence_bundle",
                "label": "Configured evidence bundle",
                "status": "\(closurePacketConfiguredBundleStatus)",
                "command": "make configured-live-evidence-bundle",
                "detail": "Build configured live evidence bundle after resource and provider evidence are ready.",
                "required": true,
                "actions": [
                  {
                    "id": "configured_live_evidence_bundle",
                    "label": "Configured live evidence bundle",
                    "status": "\(closurePacketConfiguredBundleStatus)",
                    "command": "\(closurePacketConfiguredBundleCommand)",
                    "detail": "\(closurePacketConfiguredBundleDetail)",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ],
                "first_action": {
                  "id": "configured_live_evidence_bundle",
                  "label": "Configured live evidence bundle",
                  "status": "\(closurePacketConfiguredBundleStatus)",
                  "command": "\(closurePacketConfiguredBundleCommand)",
                  "detail": "\(closurePacketConfiguredBundleDetail)",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["configured_live_evidence_bundle"],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              },
              {
                "id": "final_acceptance",
                "label": "Final acceptance",
                "status": "partial",
                "command": "make final-showcase-readiness",
                "detail": "Rerun final acceptance and showcase readiness after evidence is ready.",
                "required": true,
                "actions": [
                  {
                    "id": "final_showcase_readiness",
                    "label": "Final showcase readiness",
                    "status": "partial",
                    "command": "make final-showcase-readiness",
                    "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
                    "required": true,
                    "secret": false,
                    "requires_user_input": false,
                    "requires_user_confirmation": false,
                    "requires_cost_consent": false,
                    "global": false,
                    "xcode_or_signing": false,
                    "live_provider_call": false,
                    "safe_local_write": false,
                    "writes_repo_local_files": false
                  }
                ],
                "first_action": {
                  "id": "final_showcase_readiness",
                  "label": "Final showcase readiness",
                  "status": "partial",
                  "command": "make final-showcase-readiness",
                  "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": [],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              }
            ],
            "sections_by_id": {
              "resource_inputs": {
                "id": "resource_inputs",
                "label": "Resource inputs",
                "status": "blocked",
                "command": "make final-resource-fill-guide",
                "detail": "Fill required final resource inputs.",
                "required": true,
                "actions": [],
                "first_action": {
                  "id": "provide_MESHY_API_KEY",
                  "label": "Meshy API key",
                  "status": "missing",
                  "command": "\(closurePacketActionCommand)",
                  "detail": "\(closurePacketActionDetail)",
                  "required": true,
                  "secret": true,
                  "requires_user_input": true,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["provide_MESHY_API_KEY"],
                "requires_user_input": true,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              },
              "device_evidence": {
                "id": "device_evidence",
                "label": "Device evidence",
                "status": "blocked",
                "command": "make ios-device-launch-rehearsal",
                "detail": "Collect backend LAN, deploy preflight, Xcode, and rehearsal proof.",
                "required": true,
                "actions": [],
                "first_action": {
                  "id": "mobile_deploy_preflight",
                  "label": "Mobile deploy preflight",
                  "status": "blocked",
                  "command": "make mobile-deploy-preflight",
                  "detail": "Run mobile deploy preflight after backend-device-demo is reachable.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["mobile_deploy_preflight"],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              },
              "live_provider_consent": {
                "id": "live_provider_consent",
                "label": "Live provider consent",
                "status": "live",
                "command": "make live-provider-evidence",
                "detail": "Run Meshy, OpenAI, and print-provider evidence only after cost consent.",
                "required": false,
                "actions": [],
                "first_action": {
                  "id": "run_live_provider_evidence",
                  "label": "Refresh live provider evidence",
                  "status": "live",
                  "command": "make live-provider-evidence",
                  "detail": "Refresh configured Meshy/OpenAI evidence after cost consent.",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": true,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": true,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": [],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": true,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": true,
                "safe_local_write": false
              },
              "configured_evidence_bundle": {
                "id": "configured_evidence_bundle",
                "label": "Configured evidence bundle",
                "status": "\(closurePacketConfiguredBundleStatus)",
                "command": "make configured-live-evidence-bundle",
                "detail": "Build configured live evidence bundle after resource and provider evidence are ready.",
                "required": true,
                "actions": [],
                "first_action": {
                  "id": "configured_live_evidence_bundle",
                  "label": "Configured live evidence bundle",
                  "status": "\(closurePacketConfiguredBundleStatus)",
                  "command": "\(closurePacketConfiguredBundleCommand)",
                  "detail": "\(closurePacketConfiguredBundleDetail)",
                  "required": true,
                  "secret": false,
                  "requires_user_input": false,
                  "requires_user_confirmation": false,
                  "requires_cost_consent": false,
                  "global": false,
                  "xcode_or_signing": false,
                  "live_provider_call": false,
                  "safe_local_write": false,
                  "writes_repo_local_files": false
                },
                "blocked_by": ["configured_live_evidence_bundle"],
                "requires_user_input": false,
                "requires_user_confirmation": false,
                "requires_cost_consent": false,
                "global_action": false,
                "xcode_or_signing": false,
                "live_provider_call": false,
                "safe_local_write": false
              }
            },
            "operator_actions": [
              "provide MESHY_API_KEY",
              "run make ios-device-launch-rehearsal",
              "approve live provider cost before make live-provider-evidence"
            ],
            "commands": [
              "make final-resource-fill-guide",
              "make final-external-action-ledger",
              "make ios-device-launch-rehearsal",
              "make live-provider-evidence",
              "make configured-live-evidence-bundle",
              "make final-showcase-readiness"
            ],
            "safety": {
              "commands_run": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "runs_shell_writers": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false,
              "describes_global_actions": true,
              "requires_cost_consent_for_live_actions": true
            }
          },
          "final_acceptance_readiness": {
            "kind": "final_acceptance_readiness_report",
            "status": "\(finalAcceptanceStatus)",
            "source_file": {
              "path": "services/backend/.local/final-acceptance-local.json",
              "exists": \(finalAcceptanceStatus == "missing" ? "false" : "true")
            },
            "freshness": {
              "status": "\(finalAcceptanceFreshnessStatus)",
              "classification": "\(finalAcceptanceFreshnessClassification)",
              "checked_against": "git_head",
              "source_modified_at": "2026-06-06T12:00:00Z",
              "current_revision": "abc1234",
              "current_revision_committed_at": "2026-06-06T12:05:00Z"
            },
            "summary": {
              "passed": \(finalAcceptanceStatus == "ready" ? "14" : "12"),
              "blocked": \(finalAcceptanceStatus == "blocked" ? "2" : "0"),
              "failed": 0,
              "skipped": 0
            },
            "blockers": \(finalAcceptanceStatus == "blocked" ? """
            [
              {
                "id": "mobile_deploy_preflight",
                "label": "iOS deploy preflight",
                "status": "blocked",
                "classification": "blocked_by_local_ios_deploy_config",
                "command": "make mobile-deploy-preflight",
                "detail": "\(finalAcceptanceBlockerDetail)"
              },
              {
                "id": "mobile_xcode_build",
                "label": "Xcode build gate",
                "status": "blocked",
                "classification": "blocked_by_apple_sdk_license",
                "command": "make mobile-xcode-build",
                "detail": "Apple SDK license remains external."
              }
            ]
            """ : "[]"),
            "operator_actions": \(finalAcceptanceStatus == "ready" ? #"["final acceptance is ready"]"# : finalAcceptanceStatus == "missing" ? #"["run make final-acceptance-local to write services/backend/.local/final-acceptance-local.json"]"# : #"["provide iOS deploy config and rerun mobile deploy preflight", "resolve Xcode build gate outside the app"]"#),
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "global_mutation": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "three_d_evaluation_readiness": {
            "kind": "three_d_evaluation_readiness_report",
            "status": "\(threeDEvaluationStatus)",
            "source_file": {
              "path": "services/backend/.local/3d-evaluation-local.json",
              "exists": \(threeDEvaluationStatus == "missing" ? "false" : "true")
            },
            "summary": {
              "total_cases": \(threeDEvaluationStatus == "missing" ? "0" : "20"),
              "succeeded": \(threeDEvaluationStatus == "ready" ? "20" : "0"),
              "failed": \(threeDEvaluationStatus == "blocked" ? "1" : "0")
            },
            "coverage": {
              "input_modes": {
                "text_prompt": \(threeDEvaluationStatus == "ready" ? "20" : "0"),
                "single_image": 0,
                "multi_image": 0,
                "unknown": 0
              },
              "variant_roles": \(threeDEvaluationStatus == "ready" ? #"{"game_asset": 20, "ios_scene_asset": 20}"# : #"{}"#),
              "scene_loadable_cases": \(threeDEvaluationStatus == "ready" ? "20" : "0")
            },
            "blockers": \(threeDEvaluationStatus == "blocked" ? """
            [
              {
                "id": "three_d_evaluation",
                "label": "3D evaluation",
                "status": "failed",
                "classification": "\(threeDEvaluationBlockerClassification)",
                "command": "cd services/backend && uv run python -m myth_forge_api.cli evaluate-3d --provider local --suite default-v0 --output .local/3d-evaluation-local.json",
                "detail": "\(threeDEvaluationBlockerDetail)"
              }
            ]
            """ : "[]"),
            "operator_actions": \(threeDEvaluationStatus == "ready" ? #"["3D evaluation is ready"]"# : threeDEvaluationStatus == "missing" ? #"["run local 3D evaluation with evaluate-3d and write services/backend/.local/3d-evaluation-local.json"]"# : #"["rerun local 3D evaluation and review failed cases"]"#),
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "global_mutation": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "local_paths_in_report": false,
              "payment_links_in_report": false
            }
          },
          "visual_regression_readiness": {
            "kind": "visual_regression_readiness_report",
            "status": "\(visualRegressionStatus)",
            "source_file": {
              "path": "services/backend/.local/visual-regression-local.json",
              "exists": \(visualRegressionStatus == "missing" ? "false" : "true")
            },
            "freshness": {
              "status": "\(visualRegressionFreshnessStatus)",
              "classification": "\(visualRegressionFreshnessClassification)",
              "checked_against": "git_head",
              "source_modified_at": "2026-06-07T12:05:00Z",
              "current_revision": "abc1234",
              "current_revision_committed_at": "2026-06-07T12:00:00Z"
            },
            "summary": {
              "passed": \(visualRegressionStatus == "ready" ? "1" : "0"),
              "failed": \(visualRegressionStatus == "blocked" ? "1" : "0")
            },
            "artifacts": [
              {
                "id": "p0.118_scene_load_proof",
                "status": "\(visualRegressionStatus == "ready" ? "passed" : "failed")",
                "html_path": "docs/superpowers/verification/p0.118-scene-load-proof.html",
                "png_path": "docs/superpowers/verification/assets/p0.118-scene-load-proof-390x844.png"
              }
            ],
            "blockers": \(visualRegressionStatus == "blocked" ? """
            [
              {
                "id": "visual_regression",
                "label": "Visual regression",
                "status": "failed",
                "classification": "\(visualRegressionBlockerClassification)",
                "command": "make visual-regression-local",
                "detail": "\(visualRegressionBlockerDetail)"
              }
            ]
            """ : "[]"),
            "operator_actions": \(visualRegressionStatus == "ready" ? #"[]"# : "[\"\(visualRegressionAction)\"]"),
            "commands": [
              "make visual-regression-local",
              "cd services/backend && uv run python -m myth_forge_api.cli visual-regression --repo-root ../.. --output .local/visual-regression-local.json"
            ],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "local_showcase_smoke": {
            "kind": "local_showcase_smoke_report",
            "status": "\(localShowcaseSmokeStatus)",
            "summary": \(localSmokeSummaryJSON),
            "steps": \(localSmokeStepsJSON),
            "session": {
              "session_id": "myth_local_showcase_001",
              "generated_asset_provider": "local_stub",
              "generation_input_mode": "multi_image",
              "scene_variant_format": "dae"
            },
            "npc": {
              "completed_steps": \(localSmokeSucceeded ? "2" : "0"),
              "latest_tick_id": "\(localSmokeSucceeded ? "tick_002" : "")"
            },
            "print": {
              "quote_status": "\(localSmokeSucceeded ? "draft_quote" : "not_requested")",
              "provider": "local_stub"
            },
            "downloads": {
              "game_glb": {
                "status": "\(localSmokeSucceeded ? "passed" : "skipped")",
                "content_proof": "\(localSmokeSucceeded ? "glTF" : "")"
              },
              "scene_dae": {
                "status": "\(localSmokeSucceeded ? "passed" : "skipped")",
                "content_proof": "\(localSmokeSucceeded ? "COLLADA" : "")"
              },
              "print_3mf": {
                "status": "\(localSmokeSucceeded ? "passed" : "skipped")",
                "content_proof": "\(localSmokeSucceeded ? "PK" : "")"
              }
            },
            "safety": {
              "provider_calls": false,
              "live_provider_calls": false,
              "global_mutation": false,
              "starts_server": false,
              "writes_repo_local_media": false,
              "uses_temporary_storage": true,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "local_paths_in_report": false,
              "payment_links_in_report": false
            }
          },
          "live_provider_evidence": {
            "kind": "live_provider_evidence_report",
            "status": "\(liveProviderEvidenceStatus)",
            "summary": \(liveEvidenceSummaryJSON),
            "first_blocker": \(liveEvidenceFirstBlockerJSON),
            "evidence": [
              {
                "id": "\(liveEvidenceFirstID)",
                "label": "\(liveEvidenceFirstLabel)",
                "status": "\(liveEvidenceFirstStatus)",
                "classification": "\(liveEvidenceFirstClassification)",
                "command": "\(liveEvidenceCommand)",
                "detail": "\(liveProviderEvidenceBlockerDetail)",
                "requires_live_provider_consent": \(liveEvidenceBlocked ? "true" : "false")
              }
            ],
            "operator_actions": \(liveEvidenceReady ? #"[]"# : #"["run make live-provider-evidence after configured provider evidence files are refreshed"]"#),
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "local_paths_in_report": false,
              "payment_links_in_report": false
            }
          },
          "final_configured_evidence_plan": {
            "kind": "final_configured_evidence_plan_report",
            "status": "\(configuredEvidencePlanStatus)",
            "summary": \(configuredEvidencePlanSummaryJSON),
            "steps": [
              {
                "id": "three_d_evaluation_configured",
                "label": "Configured 3D evaluation",
                "status": "\(configuredEvidencePlanStepStatus)",
                "command": "make backend-evaluate-3d-configured",
                "requires_live_provider_consent": true,
                "may_call_live_provider": true,
                "cost_risk": true,
                "repo_local_write": true,
                "would_write_backend_env": false,
                "would_write_ios_deploy_config": false,
                "blocked_by": \(configuredEvidencePlanReady ? "[]" : #"["MESHY_API_KEY", "PMF_ALLOW_LIVE_PROVIDER_CALLS"]"#),
                "evidence_status": "\(configuredEvidencePlanStepStatus)",
                "evidence_path": "services/backend/.local/3d-evaluation-configured.json",
                "evidence_detail": "\(configuredEvidencePlanBlockerDetail)"
              }
            ],
            "steps_by_id": {
              "three_d_evaluation_configured": {
                "id": "three_d_evaluation_configured",
                "label": "Configured 3D evaluation",
                "status": "\(configuredEvidencePlanStepStatus)",
                "command": "make backend-evaluate-3d-configured",
                "requires_live_provider_consent": true,
                "may_call_live_provider": true,
                "cost_risk": true,
                "repo_local_write": true,
                "would_write_backend_env": false,
                "would_write_ios_deploy_config": false,
                "blocked_by": \(configuredEvidencePlanReady ? "[]" : #"["MESHY_API_KEY", "PMF_ALLOW_LIVE_PROVIDER_CALLS"]"#),
                "evidence_status": "\(configuredEvidencePlanStepStatus)",
                "evidence_path": "services/backend/.local/3d-evaluation-configured.json",
                "evidence_detail": "\(configuredEvidencePlanBlockerDetail)"
              }
            },
            "operator_actions": \(configuredEvidencePlanOperatorActionsJSON),
            "commands": [
              "make final-configured-evidence-plan",
              "make live-provider-evidence"
            ],
            "live_call_policy": {
              "live_calls_by_default": false,
              "allow_live_provider_calls": false,
              "consent_flag": "PMF_ALLOW_LIVE_PROVIDER_CALLS",
              "consent_required_for": ["three_d_evaluation_configured", "print_quote_configured"]
            },
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "configured_live_evidence_bundle": {
            "kind": "configured_live_evidence_bundle_report",
            "status": "\(configuredEvidenceBundleStatus)",
            "summary": \(configuredEvidenceBundleSummaryJSON),
            "current_blocker": \(configuredEvidenceBundleBlockerJSON),
            "evidence_files": [
              {
                "id": "provider_handoff",
                "label": "Provider handoff",
                "path": "services/backend/.local/provider-handoff.json",
                "status": "\(configuredEvidenceBundleReady ? "ready" : "missing")",
                "classification": "\(configuredEvidenceBundleReady ? "ready" : "missing_report")",
                "expected_kind": "provider_handoff_report",
                "command": "make provider-handoff",
                "requires_live_provider_consent": false,
                "detail": "\(configuredEvidenceBundleReady ? "Meshy and OpenAI core provider config is real-provider-ready." : "Missing provider handoff.")"
              }
            ],
            "command_sequence": [
              {
                "id": "final_resource_fill_guide",
                "label": "Final resource fill guide",
                "status": "\(configuredEvidenceBundleReady ? "ready" : "blocked")",
                "command": "make final-resource-fill-guide",
                "requires_live_provider_consent": false,
                "may_call_live_provider": false,
                "cost_risk": false,
                "repo_local_write": false,
                "would_write_backend_env": false,
                "would_write_ios_deploy_config": false,
                "blocked_by": \(configuredEvidenceBundleReady ? "[]" : #"["MESHY_API_KEY"]"#)
              }
            ],
            "operator_actions": \(configuredEvidenceBundleOperatorActionsJSON),
            "commands": ["make configured-live-evidence-bundle"],
            "live_call_policy": {
              "bundle_calls_live_providers": false,
              "live_calls_by_default": false,
              "allow_live_provider_calls": false,
              "consent_flag": "--allow-live-provider-calls",
              "consent_required_for": ["three_d_evaluation_configured"]
            },
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "print_fulfillment_readiness": {
            "kind": "print_fulfillment_readiness_report",
            "status": "\(printFulfillmentReadinessStatus)",
            "summary": \(printReadinessSummaryJSON),
            "checks": [
              {
                "id": "print_quote_acceptance",
                "label": "Local print quote acceptance",
                "status": "ready",
                "classification": "local_draft_quote_ready",
                "command": "cd services/backend && uv run pytest tests/test_print_acceptance.py",
                "detail": "Deterministic local print candidate and draft quote are ready.",
                "evidence": ["provider:local_stub", "format:3mf"]
              },
              {
                "id": "configured_treatstock_quote",
                "label": "Configured Treatstock quote",
                "status": "\(printReadinessFirstStatus)",
                "classification": "\(printReadinessFirstClassification)",
                "command": "make print-fulfillment-readiness",
                "detail": "\(printFulfillmentReadinessBlockerDetail)",
                "evidence": ["provider:treatstock"]
              }
            ],
            "first_blocker": \(printReadinessFirstBlockerJSON),
            "operator_actions": \(printReadinessReady ? #"[]"# : "[\"\(printFulfillmentReadinessAction)\"]"),
            "commands": ["make print-fulfillment-readiness"],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "final_showcase_readiness": {
            "kind": "final_showcase_readiness_report",
            "status": "\(finalShowcaseReadinessStatus)",
            "summary": {
              "ready": \(finalShowcaseReadinessStatus == "ready" ? "8" : "5"),
              "partial": \(finalShowcaseReadinessStatus == "partial" ? "3" : "0"),
              "blocked": \(finalShowcaseReadinessStatus == "blocked" ? "1" : "0")
            },
            "capabilities": [
              {
                "id": "ios_deployable",
                "label": "iOS deployable",
                "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                "classification": "ios_deploy_evidence",
                "required": true,
                "evidence": ["ios_deploy_runbook:partial", "ios_device_launch_rehearsal_readiness:missing"],
                "command": "make ios-device-launch-rehearsal",
                "detail": "\(finalShowcaseReadinessFirstBlockerDetail)"
              },
              {
                "id": "capture_scanning",
                "label": "Capture and scanning",
                "status": "ready",
                "classification": "source_acceptance_passed",
                "required": true,
                "evidence": ["source_features:6"],
                "command": "cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py",
                "detail": "iOS source acceptance covers camera, guided scan, ARKit scan, and capture-to-3D review."
              }
            ],
            "first_blocker": \(finalShowcaseReadinessStatus == "ready" ? "null" : """
            {
              "id": "ios_deployable",
              "label": "iOS deployable",
              "status": "\(finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
              "classification": "ios_deploy_evidence",
              "required": true,
              "evidence": ["ios_deploy_runbook:partial"],
              "command": "make ios-device-launch-rehearsal",
              "detail": "\(finalShowcaseReadinessFirstBlockerDetail)"
            }
            """),
            "next_action": \(finalShowcaseReadinessStatus == "ready" ? "null" : """
            {
              "id": "ios_deployable",
              "label": "iOS deployable",
              "status": "\(finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
              "classification": "ios_deploy_evidence",
              "command": "make ios-device-launch-rehearsal",
              "detail": "\(finalShowcaseReadinessFirstBlockerDetail)",
              "source": "first_blocker"
            }
            """),
            "device_action_bundle": {
              "id": "ios_device_manual_actions",
              "label": "iOS Device Manual Actions",
              "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
              "summary": {
                "actions": 4,
                "ready": \(finalShowcaseReadinessStatus == "ready" ? "4" : "0"),
                "manual": 4,
                "blocked": \(finalShowcaseReadinessStatus == "blocked" ? "4" : "0"),
                "partial": \(finalShowcaseReadinessStatus == "partial" ? "4" : "0"),
                "xcode_or_signing": 1,
                "global_actions": 0,
                "provider_calls": 0
              },
              "first_action": {
                "id": "start_backend_device_demo",
                "label": "Start backend device demo",
                "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                "classification": "manual_backend_required",
                "command": "make backend-device-demo",
                "detail": "Start the LAN-reachable backend before running iPhone preflight.",
                "source": "final_showcase_readiness",
                "evidence_status": "blocked",
                "evidence_source": "services/backend/.local/mobile-deploy-preflight-evidence.json",
                "evidence_detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
                "validation_command": "make mobile-deploy-preflight-evidence",
                "blocks": ["ios_deployable", "functional_regression"],
                "manual": true,
                "global_action": false,
                "provider_calls": false,
                "xcode_or_signing": false
              },
              "actions": [
                {
                  "id": "start_backend_device_demo",
                  "label": "Start backend device demo",
                  "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                  "classification": "manual_backend_required",
                  "command": "make backend-device-demo",
                  "detail": "Start the LAN-reachable backend before running iPhone preflight.",
                  "source": "final_showcase_readiness",
                  "evidence_status": "blocked",
                  "evidence_source": "services/backend/.local/mobile-deploy-preflight-evidence.json",
                  "evidence_detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
                  "validation_command": "make mobile-deploy-preflight-evidence",
                  "blocks": ["ios_deployable", "functional_regression"],
                  "manual": true,
                  "global_action": false,
                  "provider_calls": false,
                  "xcode_or_signing": false
                },
                {
                  "id": "run_mobile_deploy_preflight",
                  "label": "Run mobile deploy preflight",
                  "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                  "classification": "manual_preflight_required",
                  "command": "make mobile-deploy-preflight",
                  "detail": "Verify the iPhone can reach the backend and read launch config.",
                  "source": "final_showcase_readiness",
                  "evidence_status": "blocked",
                  "evidence_source": "services/backend/.local/mobile-deploy-preflight-evidence.json",
                  "evidence_detail": "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable",
                  "validation_command": "make mobile-deploy-preflight-evidence",
                  "blocks": ["ios_deployable", "functional_regression"],
                  "manual": true,
                  "global_action": false,
                  "provider_calls": false,
                  "xcode_or_signing": false
                },
                {
                  "id": "resolve_xcode_build_gate",
                  "label": "Resolve Xcode build gate",
                  "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                  "classification": "manual_xcode_or_signing_required",
                  "command": "open Xcode and resolve signing/build gate",
                  "detail": "Resolve signing or build issues in Xcode before device launch proof.",
                  "source": "final_showcase_readiness",
                  "evidence_status": "blocked",
                  "evidence_source": "services/backend/.local/mobile-xcode-build-evidence.json",
                  "evidence_detail": "Apple SDK license agreement is not accepted.",
                  "validation_command": "make mobile-xcode-build-evidence",
                  "blocks": ["ios_deployable"],
                  "manual": true,
                  "global_action": false,
                  "provider_calls": false,
                  "xcode_or_signing": true
                },
                {
                  "id": "run_ios_device_launch_rehearsal",
                  "label": "Run iOS device launch rehearsal",
                  "status": "\(finalShowcaseReadinessStatus == "ready" ? "ready" : finalShowcaseReadinessStatus == "blocked" ? "blocked" : "partial")",
                  "classification": "manual_device_rehearsal_required",
                  "command": "make ios-device-launch-rehearsal",
                  "detail": "Refresh the final iOS device rehearsal evidence after preflight passes.",
                  "source": "final_showcase_readiness",
                  "blocks": ["ios_deployable"],
                  "manual": true,
                  "global_action": false,
                  "provider_calls": false,
                  "xcode_or_signing": false
                }
              ],
              "safety": {
                "commands_run": false,
                "global_mutation": false,
                "provider_calls": false,
                "live_provider_calls": false,
                "writes_backend_env": false,
                "writes_ios_deploy_config": false,
                "xcode_or_signing": false,
                "keychain_writes": false
              }
            },
            "operator_actions": \(finalShowcaseActionsJSON),
            "commands": [
              "make final-rehearsal-local",
              "make final-showcase-readiness"
            ],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "npc_agent_evaluation_readiness": {
            "kind": "npc_agent_evaluation_readiness_report",
            "status": "\(npcEvaluationStatus)",
            "source_file": {
              "path": "services/backend/.local/npc-evaluation-local.json",
              "exists": \(npcEvaluationStatus == "missing" ? "false" : "true")
            },
            "summary": {
              "total_cases": \(npcEvaluationStatus == "missing" ? "0" : "6"),
              "succeeded": \(npcEvaluationStatus == "ready" ? "6" : "0"),
              "failed": \(npcEvaluationStatus == "blocked" ? "1" : "0"),
              "tick_steps": \(npcEvaluationStatus == "missing" ? "0" : "2")
            },
            "coverage": {
              "expected_npc_sets": \(npcEvaluationStatus == "ready" ? "6" : "0"),
              "trace_sets": \(npcEvaluationStatus == "ready" ? "6" : "0"),
              "proposed_action_plan_matches": \(npcEvaluationStatus == "ready" ? "6" : "0"),
              "tick_steps_completed": \(npcEvaluationStatus == "ready" ? "12" : "0"),
              "world_resolution_steps": \(npcEvaluationStatus == "ready" ? "12" : "0")
            },
            "blockers": \(npcEvaluationStatus == "blocked" ? """
            [
              {
                "id": "npc_agent_evaluation",
                "label": "NPC Agent evaluation",
                "status": "failed",
                "classification": "\(npcEvaluationBlockerClassification)",
                "command": "cd services/backend && uv run python -m myth_forge_api.cli evaluate-npc --provider local --suite default-v0 --tick-steps 2 --output .local/npc-evaluation-local.json",
                "detail": "\(npcEvaluationBlockerDetail)"
              }
            ]
            """ : "[]"),
            "operator_actions": \(npcEvaluationStatus == "ready" ? #"["NPC Agent evaluation is ready"]"# : npcEvaluationStatus == "missing" ? #"["run local NPC Agent evaluation with evaluate-npc and write services/backend/.local/npc-evaluation-local.json"]"# : #"["rerun local NPC Agent evaluation and review failed cases"]"#),
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "global_mutation": false,
              "provider_secrets_in_report": false,
              "raw_private_context_in_report": false,
              "raw_media_in_report": false,
              "local_paths_in_report": false,
              "payment_links_in_report": false
            }
          },
          "final_operator_handoff": {
            "kind": "final_operator_handoff_report",
            "mode": "local",
            "status": "\(finalOperatorHandoffStatus)",
            "summary": {
              "ready": \(finalOperatorHandoffStatus == "ready" ? "7" : "4"),
              "missing": \(finalOperatorHandoffStatus == "missing" ? "1" : "0"),
              "blocked": \(finalOperatorHandoffStatus == "blocked" ? "1" : "0"),
              "manual": 1,
              "optional": 1,
              "partial": 0,
              "live": \(finalOperatorHandoffStatus == "live" ? "1" : "0")
            },
            "steps": [
              {
                "id": "local_final_acceptance",
                "label": "Run local final acceptance",
                "status": "\(finalOperatorHandoffStatus)",
                "command": "make final-acceptance-local",
                "required_for": "no-key deterministic smoke acceptance",
                "source": "final_acceptance_readiness",
                "notes": ["\(finalOperatorHandoffAction)"],
                "requires_consent": false
              },
              {
                "id": "configured_final_acceptance",
                "label": "Run configured final acceptance",
                "status": "\(finalOperatorHandoffStatus == "live" ? "live" : "optional")",
                "command": "cd services/backend && uv run python -m myth_forge_api.cli final-acceptance --profile quick --provider-mode configured --require-real-core --allow-live-provider-calls --repo-root ../.. --output .local/final-acceptance-configured.json",
                "required_for": "real 3D and AI NPC provider acceptance",
                "source": "final_demo_launch_phase",
                "notes": ["May call live providers and spend provider credits."],
                "requires_consent": \(finalOperatorHandoffStatus == "live" ? "true" : "false")
              }
            ],
            "next_actions": \(finalOperatorHandoffStatus == "ready" ? #"[]"# : "[\"\(finalOperatorHandoffAction)\"]"),
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "global_mutation": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false,
              "command_execution_from_app": false
            }
          },
          "ios_deploy_runbook": {
            "kind": "ios_deploy_runbook_report",
            "mode": "local",
            "status": "\(iosDeployRunbookStatus)",
            "input_slots": [
              {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "\(iosDeployRunbookSlotStatus)",
                "required": true,
                "source": "Deployment.local.xcconfig",
                "operator_action": "\(iosDeployRunbookAction)",
                "configured": \(iosDeployRunbookSlotStatus == "ready" ? "true" : "false"),
                "redacted": false,
                "classification": "\(iosDeployRunbookSlotStatus == "ready" ? "ready" : "blocked_by_ios_deploy_config")",
                "key": "PMF_BACKEND_BASE_URL",
                "expected_mode": "local"
              },
              {
                "id": "three_d_evaluation",
                "label": "3D evaluation",
                "status": "\(iosDeployRunbookThreeDSlotStatus)",
                "required": true,
                "source": "services/backend/.local/3d-evaluation-local.json",
                "operator_action": "run local 3D evaluation with evaluate-3d and write services/backend/.local/3d-evaluation-local.json",
                "configured": \(iosDeployRunbookThreeDSlotStatus == "ready" ? "true" : "false"),
                "redacted": false,
                "classification": "\(iosDeployRunbookThreeDSlotStatus == "ready" ? "ready" : iosDeployRunbookThreeDSlotStatus == "missing" ? "missing_required_value" : "three_d_evaluation_failed")"
              },
              {
                "id": "development_team",
                "label": "Development team",
                "status": "ready",
                "required": true,
                "source": "Deployment.local.xcconfig",
                "operator_action": "set DEVELOPMENT_TEAM",
                "configured": true,
                "redacted": true,
                "classification": "ready",
                "key": "DEVELOPMENT_TEAM",
                "expected_mode": "local"
              }
            ],
            "command_sequence": [
              {
                "id": "mobile_deploy_preflight",
                "label": "Mobile deploy preflight",
                "status": "ready",
                "command": "\(iosDeployRunbookCommand)",
                "notes": ["checks iOS deploy config without touching global state"],
                "requires_consent": false
              },
              {
                "id": "mobile_xcode_build",
                "label": "Xcode build",
                "status": "blocked",
                "command": "make mobile-xcode-build",
                "notes": ["requires local Xcode and signing outside the app"],
                "requires_consent": false
              }
            ],
            "operator_actions": ["\(iosDeployRunbookAction)"],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "global_mutation": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "ios_device_evidence_bundle": {
            "kind": "ios_device_evidence_bundle_report",
            "status": "\(iosDeviceEvidenceStatus)",
            "summary": \(iosDeviceEvidenceSummaryJSON),
            "evidence_slots": [
              {
                "id": "backend_device_server",
                "label": "Backend device server",
                "status": "\(iosDeviceEvidenceReady ? "ready" : iosDeviceEvidenceSlotStatus)",
                "command": "make backend-device-demo",
                "detail": "\(iosDeviceEvidenceReady ? "Final acceptance recorded iPhone-reachable backend health." : iosDeviceEvidenceDetail)",
                "classification": "\(iosDeviceEvidenceReady ? "ready" : "backend_health_not_proven")",
                "evidence_source": "services/backend/.local/final-acceptance-local.json",
                "required": true,
                "global_action": false,
                "xcode_or_signing": false
              },
              {
                "id": "mobile_deploy_preflight",
                "label": "Mobile deploy preflight",
                "status": "\(iosDeviceEvidenceReady ? "ready" : iosDeviceEvidenceSlotStatus)",
                "command": "\(iosDeviceEvidenceCommand)",
                "detail": "\(iosDeviceEvidenceReady ? "Final acceptance recorded a passing mobile deploy preflight." : iosDeviceEvidenceDetail)",
                "classification": "\(iosDeviceEvidenceReady ? "ready" : "mobile_deploy_preflight_not_proven")",
                "evidence_source": "services/backend/.local/final-acceptance-local.json",
                "required": true,
                "global_action": false,
                "xcode_or_signing": false
              },
              {
                "id": "xcode_build_gate",
                "label": "Xcode build gate",
                "status": "\(iosDeviceEvidenceReady ? "ready" : "blocked")",
                "command": "make mobile-xcode-build",
                "detail": "\(iosDeviceEvidenceReady ? "Final acceptance recorded a passing Xcode build gate." : "Run the Xcode build gate on the Mac after deploy preflight passes.")",
                "classification": "\(iosDeviceEvidenceReady ? "ready" : "xcode_build_gate_not_proven")",
                "evidence_source": "services/backend/.local/final-acceptance-local.json",
                "required": true,
                "global_action": true,
                "xcode_or_signing": true
              },
              {
                "id": "ios_device_launch_rehearsal",
                "label": "iOS device launch rehearsal",
                "status": "\(iosDeviceEvidenceReady ? "ready" : "blocked")",
                "command": "make ios-device-launch-rehearsal",
                "detail": "\(iosDeviceEvidenceReady ? "Saved iOS device launch rehearsal evidence is ready." : "Run iOS device launch rehearsal to refresh final device evidence.")",
                "classification": "\(iosDeviceEvidenceReady ? "ready" : "blocked_rehearsal")",
                "evidence_source": "services/backend/.local/ios-device-launch-rehearsal.json",
                "required": true,
                "global_action": false,
                "xcode_or_signing": false
              }
            ],
            "operator_actions": ["\(iosDeviceEvidenceAction)"],
            "commands": [
              "make backend-device-demo",
              "make mobile-deploy-preflight",
              "make mobile-xcode-build",
              "make ios-device-launch-rehearsal"
            ],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false,
              "describes_global_actions": true
            }
          },
          "ios_device_launch_rehearsal_readiness": {
            "kind": "ios_device_launch_rehearsal_readiness_report",
            "status": "\(iosDeviceLaunchRehearsalStatus)",
            "source_file": {
              "path": "services/backend/.local/ios-device-launch-rehearsal.json",
              "exists": \(iosDeviceLaunchRehearsalStatus == "missing" ? "false" : "true")
            },
            "freshness": {
              "status": "\(iosDeviceLaunchRehearsalFreshnessStatus)",
              "classification": "\(iosDeviceLaunchRehearsalFreshnessClassification)",
              "checked_against": "git_head",
              "source_modified_at": "\(iosDeviceLaunchRehearsalFreshnessSourceModifiedAt)",
              "current_revision": "\(iosDeviceLaunchRehearsalFreshnessCurrentRevision)",
              "current_revision_committed_at": "2026-06-07T12:00:00Z"
            },
            "summary": {
              "ready": \(iosDeviceLaunchRehearsalStatus == "ready" ? "4" : "3"),
              "missing": \(iosDeviceLaunchRehearsalStatus == "missing" ? "1" : "0"),
              "blocked": \(iosDeviceLaunchRehearsalStatus == "blocked" ? "1" : "0"),
              "partial": \(iosDeviceLaunchRehearsalStatus == "partial" ? "1" : "0"),
              "manual": 0,
              "live": 0
            },
            "sequence": \(iosDeviceLaunchRehearsalStatus == "missing" ? "[]" : """
            [
              {
                "id": "final_handoff_index",
                "label": "Final handoff index",
                "status": "\(iosDeviceLaunchRehearsalStatus == "ready" ? "ready" : "blocked")",
                "command": "\(iosDeviceLaunchRehearsalCommand)",
                "detail": "\(iosDeviceLaunchRehearsalDetail)",
                "classification": "saved_report",
                "freshness_status": "\(iosDeviceLaunchSourceFreshnessStatus)",
                "freshness_classification": "\(iosDeviceLaunchSourceFreshnessClassification)",
                "freshness_summary": \(iosDeviceLaunchSourceFreshnessSummaryJSON)
              }
            ]
            """),
            "blockers": [],
            "operator_actions": \(iosDeviceLaunchActionsJSON),
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "live_provider_calls": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "ios_device_launch_certificate": {
            "kind": "ios_device_launch_certificate_report",
            "status": "\(iosDeviceLaunchCertificateStatus)",
            "mode": "local",
            "summary": {
              "ready": \(iosDeviceLaunchCertificateReady ? "8" : "4"),
              "missing": \(iosDeviceLaunchCertificateStatus == "missing" ? "1" : "0"),
              "blocked": \(iosDeviceLaunchCertificateStatus == "blocked" ? "1" : "0"),
              "manual": \(iosDeviceLaunchCertificateReady ? "0" : "2"),
              "partial": \(iosDeviceLaunchCertificateStatus == "partial" ? "1" : "0"),
              "live": \(iosDeviceLaunchCertificateReady ? "0" : "1")
            },
            "certificate": {
              "development_team": {
                "key": "DEVELOPMENT_TEAM",
                "status": "\(iosDeviceLaunchCertificateReady ? "ready" : "missing")",
                "configured": \(iosDeviceLaunchCertificateReady ? "true" : "false"),
                "source": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "redacted": \(iosDeviceLaunchCertificateReady ? "true" : "false")
              },
              "product_bundle_identifier": {
                "key": "PRODUCT_BUNDLE_IDENTIFIER",
                "status": "ready",
                "configured": true,
                "source": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "redacted": true
              },
              "backend_base_url": {
                "key": "PMF_BACKEND_BASE_URL",
                "status": "\(iosDeviceLaunchCertificateReady ? "ready" : "blocked")",
                "configured": \(iosDeviceLaunchCertificateReady ? "true" : "false"),
                "source": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "redacted": true,
                "classification": "\(iosDeviceLaunchCertificateReady ? "ready" : "loopback_url")"
              },
              "final_launch_mode": {
                "key": "PMF_FINAL_LAUNCH_MODE",
                "status": "ready",
                "configured": true,
                "mode": "local",
                "source": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                "redacted": false
              }
            },
            "device_gates": [
              {
                "id": "final_handoff_index",
                "label": "Final handoff index",
                "status": "\(iosDeviceLaunchCertificateGateEffectiveStatus)",
                "command": "make final-handoff-index",
                "required": true,
                "requires_consent": false,
                "notes": ["Refreshes the unified local/configured handoff index."]
              },
              {
                "id": "ios_deploy_config",
                "label": "iOS deploy config",
                "status": "\(iosDeviceLaunchCertificateGateEffectiveStatus)",
                "command": "make mobile-deploy-preflight",
                "required": true,
                "requires_consent": false,
                "notes": ["Requires Team ID, bundle id, final launch mode, and LAN backend URL."]
              },
              {
                "id": "backend_device_server",
                "label": "Backend device server",
                "status": "\(iosDeviceLaunchCertificateReady ? "ready" : "manual")",
                "command": "make backend-device-demo",
                "required": false,
                "requires_consent": false,
                "notes": ["Starts FastAPI on 0.0.0.0:8080 for iPhone LAN access."]
              },
              {
                "id": "configured_final_acceptance",
                "label": "Configured final acceptance",
                "status": "\(iosDeviceLaunchCertificateReady ? "ready" : "live")",
                "command": "make final-acceptance-configured",
                "required": false,
                "requires_consent": \(iosDeviceLaunchCertificateReady ? "false" : "true"),
                "notes": ["May call live providers and spend provider credits."]
              }
            ],
            "operator_actions": \(iosDeviceLaunchCertificateActionsJSON),
            "commands": [
              "make ios-device-launch-certificate",
              "make final-handoff-index",
              "make backend-device-demo",
              "make mobile-deploy-preflight"
            ],
            "safety": {
              "commands_run": false,
              "provider_calls": false,
              "writes_local_config": false,
              "writes_backend_env": false,
              "writes_ios_deploy_config": false,
              "global_mutation": false,
              "xcode_or_signing": false,
              "keychain_writes": false,
              "provider_secrets_in_report": false,
              "raw_media_in_report": false,
              "payment_links_in_report": false,
              "local_paths_in_report": false
            }
          },
          "resource_report": {
            "kind": "resource_handoff_report",
            "overall_status": "\(resourceHandoffStatus)",
            "summary": {
              "ready": \(resourceHandoffStatus == "ready" ? "9" : "2"),
              "missing": \(resourceHandoffStatus == "ready" ? "0" : "4"),
              "blocked": \(resourceHandoffStatus == "ready" ? "0" : "1"),
              "manual": \(resourceHandoffStatus == "ready" ? "0" : "1"),
              "optional": 1
            },
            "backend": {
              "destination": "\(resourceHandoffDestination)",
              "items": [
                {
                  "id": "MESHY_API_KEY",
                  "label": "Meshy API key",
                  "destination": "\(resourceHandoffDestination)",
                  "required_for": "real text/image/multi-image 3D generation",
                  "status": "\(resourceHandoffBackendStatus)",
                  "configured": \(resourceHandoffBackendStatus == "ready" ? "true" : "false"),
                  "missing": \(resourceHandoffBackendStatus == "missing" ? "true" : "false"),
                  "notes": ["Backend-only key; never put it in the iOS app."]
                },
                {
                  "id": "OPENAI_API_KEY",
                  "label": "OpenAI API key",
                  "destination": "\(resourceHandoffDestination)",
                  "required_for": "AI Agent NPC traces and ticks",
                  "status": "\(resourceHandoffBackendStatus)",
                  "configured": \(resourceHandoffBackendStatus == "ready" ? "true" : "false"),
                  "missing": \(resourceHandoffBackendStatus == "missing" ? "true" : "false"),
                  "notes": ["Backend-only key; mobile sees only generated NPC state."]
                }
              ]
            },
            "ios": {
              "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
              "items": [
                {
                  "id": "PMF_BACKEND_BASE_URL",
                  "label": "iPhone-reachable backend URL",
                  "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                  "required_for": "device-to-Mac backend calls",
                  "status": "\(resourceHandoffIOSStatus)",
                  "configured": \(resourceHandoffIOSStatus == "ready" ? "true" : "false"),
                  "missing": \(resourceHandoffIOSStatus == "missing" ? "true" : "false"),
                  "notes": ["Use a LAN URL such as http://192.168.1.10:8080, not loopback."]
                },
                {
                  "id": "DEVELOPMENT_TEAM",
                  "label": "Apple development team",
                  "destination": "apps/mobile/ios/Config/Deployment.local.xcconfig",
                  "required_for": "iPhone signing",
                  "status": "\(resourceHandoffIOSStatus == "ready" ? "ready" : "missing")",
                  "configured": \(resourceHandoffIOSStatus == "ready" ? "true" : "false"),
                  "missing": \(resourceHandoffIOSStatus == "ready" ? "false" : "true"),
                  "notes": ["Copy Deployment.local.xcconfig.example and fill your Apple Team ID."]
                }
              ]
            },
            "operator_actions": ["\(resourceHandoffAction)"],
            "commands": ["make final-apply-resources"],
            "safety": {
              "provider_secrets_in_report": false,
              "local_paths_in_report": false,
              "payment_links_in_report": false
            }
          },
          "launch_phases": [
            {
              "id": "backend_device_server",
              "label": "Start backend on LAN",
              "status": "ready",
              "required_for": "iPhone-to-Mac API calls",
              "command": "make backend-device-demo",
              "notes": ["No global state changes."]
            },
            {
              "id": "final_launch",
              "label": "Final Launch",
              "status": "\(overallStatus)",
              "required_for": "operator readiness",
              "command": "make final-demo-launch",
              "notes": ["\(unsafeDetail)"]
            }
          ],
          "operator_checklist": ["set PMF_BACKEND_BASE_URL to a LAN URL"],
          "commands": \(commandsJSON),
          "live_call_policy": {
            "live_calls_by_default": false,
            "configured_acceptance_requires_consent": true,
            "consent_flag": "--allow-live-provider-calls"
          },
          "safety": {
            "provider_secrets_in_report": false,
            "local_paths_in_report": false,
            "payment_links_in_report": false,
            "global_mutation": false,
            "live_provider_calls_by_default": false
          }
        }
        """.utf8
    )
}

private func testCreatePrintQuoteSanitizesCheckoutHTTPErrorBody() async throws {
    let body = "api_key=treatstock-secret checkout_url=https://pay.example/private token=print-secret"
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 502, data: Data(body.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createPrintQuote(printCandidate: samplePrintCandidate())
        throw ContractTestError.expectationFailed("Expected print quote HTTP status error")
    } catch let ForgeFlowError.httpStatus(status, sanitizedBody) {
        try expectEqual(status, 502)
        try expectContains(sanitizedBody, "api_key=[redacted]")
        try expectContains(sanitizedBody, "checkout_url=[redacted]")
        try expectContains(sanitizedBody, "token=[redacted]")
        try expectNotContains(sanitizedBody, "treatstock-secret")
        try expectNotContains(sanitizedBody, "https://pay.example/private")
        try expectNotContains(sanitizedBody, "print-secret")
    }
}

private func testGetMythSessionBuildsGETRequest() async throws {
    let session = try backendHistorySession()
    let data = try PMFJSON.encoder.encode(session)
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: data)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let result = try await client.getMythSession(sessionId: session.sessionId)

    try expectEqual(result.sessionId, session.sessionId)
    let request = try require(transport.requests.first, "missing myth session request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/myth-sessions/\(session.sessionId)")
    try expectEqual(request.httpBody, nil)
}

private func testGetMythSessionHistoryBuildsGETRequest() async throws {
    let session = try backendHistorySession()
    let history = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: [npcTick(sessionId: session.sessionId, tickIndex: 1)],
        updatedAt: "2026-06-06T12:00:00+00:00"
    )
    let data = try PMFJSON.encoder.encode(history)
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: data)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let result = try await client.getMythSessionHistory(sessionId: session.sessionId)

    try expectEqual(result, history)
    let request = try require(transport.requests.first, "missing myth session history request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/myth-sessions/\(session.sessionId)/history")
    try expectEqual(request.httpBody, nil)
}

private func testAdvanceMythSessionHistoryBuildsPOSTRequest() async throws {
    let session = try backendHistorySession()
    let history = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: [npcTick(sessionId: session.sessionId, tickIndex: 1)],
        updatedAt: "2026-06-06T12:05:00+00:00"
    )
    let data = try PMFJSON.encoder.encode(history)
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: data)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let decoded = try await client.advanceMythSessionHistory(sessionId: session.sessionId)

    try expectEqual(decoded, history)
    let request = try require(transport.requests.first, "missing advance history request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/myth-sessions/\(session.sessionId)/npc-ticks")
    try expectTrue(request.httpBody == nil)
}

private func testAdvanceMythSessionHistoryRejectsInvalidIDBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.advanceMythSessionHistory(sessionId: "../myth_0123456789abcdef")
        throw ContractTestError.expectationFailed("Expected invalid myth session id error")
    } catch ForgeFlowError.invalidMythSessionID("../myth_0123456789abcdef") {
        try expectEqual(transport.requests.count, 0)
    }
}

private func testRunMythSessionAutonomyBuildsPOSTRequest() async throws {
    let session = try backendHistorySession()
    let history = MythSessionHistory(
        sessionId: session.sessionId,
        session: session,
        npcTicks: [npcTick(sessionId: session.sessionId, tickIndex: 3)],
        updatedAt: "2026-06-06T12:10:00+00:00"
    )
    let run = NPCAutonomyRun(
        sessionId: session.sessionId,
        requestedSteps: 3,
        completedSteps: 3,
        startedTickIndex: 1,
        completedTickIndex: 3,
        agentRuntime: "local_tick_runtime",
        history: history
    )
    let data = try PMFJSON.encoder.encode(run)
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: data)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let decoded = try await client.runMythSessionAutonomy(sessionId: session.sessionId, stepCount: 3)

    try expectEqual(decoded, run)
    let request = try require(transport.requests.first, "missing autonomy run request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/myth-sessions/\(session.sessionId)/autonomy-runs")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"step_count\":3")
}

private func testRunMythSessionAutonomyRejectsInvalidIDBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.runMythSessionAutonomy(
            sessionId: "../myth_0123456789abcdef",
            stepCount: 3
        )
        throw ContractTestError.expectationFailed("Expected invalid myth session id error")
    } catch ForgeFlowError.invalidMythSessionID("../myth_0123456789abcdef") {
        try expectEqual(transport.requests.count, 0)
    }
}

private func testInvalidMythSessionIDFailsBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.getMythSession(sessionId: "../myth_0123456789abcdef")
        throw ContractTestError.expectationFailed("Expected invalid myth session id error")
    } catch ForgeFlowError.invalidMythSessionID("../myth_0123456789abcdef") {
        try expectEqual(transport.requests.count, 0)
    }
}

private func testCreateNPCAgentTickBuildsJSONRequest() async throws {
    let responseData = Data(
        """
        {
          "session_id": "myth_0123456789abcdef",
          "tick_index": 1,
          "agent_runtime": "local_tick_runtime",
          "npc_agent_traces": [],
          "npc_reactions": [],
          "world_resolution": {
            "arbitrator": "local_rules",
            "summary": "The village holds.",
            "accepted_actions": [],
            "rejected_actions": [],
            "world_state_delta": {},
            "visible_changes": ["The village studies the relic."]
          }
        }
        """.utf8
    )
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: responseData)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    let tick = try await client.createNPCAgentTick(
        session: session,
        tickIndex: 1,
        recentEvents: ["The village debate grows louder."]
    )

    try expectEqual(tick.agentRuntime, "local_tick_runtime")
    let request = try require(transport.requests.first, "missing npc tick request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/npc-ticks")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"session_id\":\"session_cap_ba02a3816bd145b4\"")
    try expectContains(body, "\"tick_index\":1")
    try expectContains(body, "\"recent_events\":[\"The village debate grows louder.\"]")
}

private func testCreateNPCAgentTickSanitizesHTTPErrorBody() async throws {
    let body = "Authorization=Bearer test-secret api_key=test-secret"
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 502, data: Data(body.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    do {
        _ = try await client.createNPCAgentTick(
            session: session,
            tickIndex: 1,
            recentEvents: []
        )
        throw ContractTestError.expectationFailed("Expected npc tick HTTP status error")
    } catch let ForgeFlowError.httpStatus(status, sanitizedBody) {
        try expectEqual(status, 502)
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "api_key=[redacted]")
        try expectNotContains(sanitizedBody, "test-secret")
    }
}

private func testUploadObjectCaptureUsesGeneratedFilenamesWithoutLocalPaths() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )

    _ = try await client.uploadObjectCapture(
        metadata: sampleMetadata(),
        media: [
            CaptureUpload(
                filename: "/Users/zhexu/Desktop/../../secret.jpg",
                contentType: "image/jpeg",
                data: Data("fake-jpeg".utf8)
            )
        ]
    )

    let request = try require(transport.requests.first, "missing upload request")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "filename=\"media_0.jpg\"")
    try expectNotContains(body, "/Users/")
    try expectNotContains(body, "../")
    try expectNotContains(body, "secret.jpg")
}

private func testUploadObjectCaptureRejectsUnsafeContentTypeBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.uploadObjectCapture(
            metadata: sampleMetadata(),
            media: [
                CaptureUpload(
                    filename: "media_0.jpg",
                    contentType: "image/jpeg\r\nX-Injected: 1",
                    data: Data("fake-jpeg".utf8)
                )
            ]
        )
        throw ContractTestError.expectationFailed("Expected unsafe content type error")
    } catch ForgeFlowError.encodingFailed(let message) {
        try expectContains(message, "Unsupported capture content type")
        try expectEqual(transport.requests.count, 0)
    }
}

private func testUploadObjectCaptureBuildsARKitScanMultipartRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )
    let draft = CaptureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough LiDAR mesh",
        source: "phone_capture",
        mode: .arkitScan,
        media: [
            captureMedia(
                filename: "/Users/zhexu/Desktop/idol mesh.glb",
                contentType: "model/gltf-binary",
                kind: .scanAsset
            )
        ]
    )
    let payload = try draft.validatedUploadPayload()

    _ = try await client.uploadObjectCapture(
        metadata: payload.metadata,
        media: payload.uploads
    )

    let request = try require(transport.requests.first, "missing upload request")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"capture_mode\":\"arkit_scan\"")
    try expectContains(body, "filename=\"scan_0.glb\"")
    try expectContains(body, "Content-Type: model/gltf-binary")
    try expectNotContains(body, "/Users/")
    try expectNotContains(body, "idol mesh.glb")
}

private func testCaptureModeIncludesGuidedScan() throws {
    try expectEqual(CaptureMode.guidedScan.rawValue, "guided_scan")
    try expectTrue(CaptureMode.allCases.contains(.guidedScan))
}

private func testCaptureDraftBuildsSinglePhotoPayload() throws {
    let draft = CaptureDraft(
        label: " old brass key ",
        materialsText: " metal, brass,  ",
        visualNotes: " worn teeth ",
        source: "phone_capture",
        mode: .singlePhoto,
        media: [
            captureMedia(filename: "/Users/zhexu/key.jpg", contentType: "image/jpeg", kind: .image)
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.label, "old brass key")
    try expectEqual(payload.metadata.materials, ["metal", "brass"])
    try expectEqual(payload.metadata.captureMode, "single_photo")
    try expectEqual(payload.metadata.visualNotes, "worn teeth")
    try expectEqual(payload.uploads.count, 1)
    try expectEqual(payload.uploads[0].contentType, "image/jpeg")
}

private func testCaptureDraftBuildsPhotoSetPayload() throws {
    let draft = CaptureDraft(
        label: "moon cup",
        materialsText: "ceramic, glaze",
        visualNotes: "",
        source: "phone_capture",
        mode: .photoSet,
        media: [
            captureMedia(filename: "front.heic", contentType: "image/heic", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "photo_set")
    try expectTrue(payload.metadata.visualNotes == nil)
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads.map(\.contentType), ["image/heic", "image/png"])
}

private func testCaptureDraftBuildsARKitScanPayload() throws {
    let draft = CaptureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough LiDAR mesh with one reference photo",
        source: "phone_capture",
        mode: .arkitScan,
        media: [
            captureMedia(filename: "idol.glb", contentType: "model/gltf-binary", kind: .scanAsset),
            captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "arkit_scan")
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads[0].contentType, "model/gltf-binary")
    try expectEqual(payload.uploads[1].contentType, "image/jpeg")
}

private func testCaptureDraftBuildsGuidedScanPayload() throws {
    let draft = CaptureDraft(
        label: "wooden fox",
        materialsText: "wood, paint",
        visualNotes: "guided scan image set",
        source: "phone_capture",
        mode: .guidedScan,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "guided_scan")
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads.map(\.contentType), ["image/jpeg", "image/png"])
}

private func testCaptureDraftRejectsInvalidMedia() throws {
    try expectCaptureDraftError(
        CaptureDraft(
            label: " ",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .missingLabel
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .arkitScan,
            media: [captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .missingScanAsset
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .photoSet,
            media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .invalidMediaCount(.photoSet, 1)
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.txt", contentType: "text/plain", kind: .image)]
        ),
        .unsupportedContentType("text/plain")
    )
}

private func testCaptureDraftRejectsInvalidGuidedScanMedia() throws {
    try expectCaptureDraftError(
        CaptureDraft(
            label: "wooden fox",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .guidedScan,
            media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .invalidMediaCount(.guidedScan, 1)
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "wooden fox",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .guidedScan,
            media: [
                captureMedia(filename: "fox.glb", contentType: "model/gltf-binary", kind: .scanAsset)
            ]
        ),
        .invalidMediaCount(.guidedScan, 1)
    )
}

private func testCaptureDraftRejectsOversizedMedia() throws {
    let limit = CaptureDraft.maxFileBytes
    try expectCaptureDraftError(
        CaptureDraft(
            label: "small idol",
            materialsText: "stone",
            visualNotes: "",
            source: "phone_capture",
            mode: .arkitScan,
            media: [
                captureMedia(
                    filename: "oversized.glb",
                    contentType: "model/gltf-binary",
                    kind: .scanAsset,
                    data: Data(repeating: 0, count: limit + 1)
                )
            ]
        ),
        .mediaTooLarge(limit + 1, limit)
    )
}

private func testCaptureMediaSelectionSummarizesSinglePhoto() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )

    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.imageCount, 1)
    try expectEqual(selection.scanAssetCount, 0)
    try expectEqual(selection.summary.title, "1 photo selected")
    try expectContains(selection.summary.detail, "key.jpg")
}

private func testCaptureMediaSelectionRequiresPhotoSetCount() throws {
    let onePhoto = CaptureMediaSelection(
        mode: .photoSet,
        media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let twoPhotos = CaptureMediaSelection(
        mode: .photoSet,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    try expectFalse(onePhoto.isReadyForUpload)
    try expectTrue(twoPhotos.isReadyForUpload)
    try expectEqual(twoPhotos.summary.title, "2 photos selected")
}

private func testCaptureMediaSelectionBuildsARKitDraft() throws {
    let selection = CaptureMediaSelection(
        mode: .arkitScan,
        media: [
            captureMedia(filename: "idol.glb", contentType: "model/gltf-binary", kind: .scanAsset),
            captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )

    let draft = selection.captureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough mesh",
        source: "phone_capture"
    )
    let payload = try draft.validatedUploadPayload()

    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.scanAssetCount, 1)
    try expectEqual(selection.imageCount, 1)
    try expectEqual(payload.metadata.captureMode, "arkit_scan")
    try expectEqual(payload.uploads.map(\.contentType), ["model/gltf-binary", "image/jpeg"])
}

private func testCaptureMediaSelectionSummarizesGuidedScan() throws {
    let emptySelection = CaptureMediaSelection(mode: .guidedScan)
    let onePhoto = CaptureMediaSelection(
        mode: .guidedScan,
        media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let twoPhotos = CaptureMediaSelection(
        mode: .guidedScan,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    try expectFalse(emptySelection.isReadyForUpload)
    try expectEqual(emptySelection.summary.title, "Choose guided scan photos")
    try expectEqual(emptySelection.summary.detail, "Choose at least 2 guided scan photos")
    try expectFalse(onePhoto.isReadyForUpload)
    try expectTrue(twoPhotos.isReadyForUpload)
    try expectEqual(twoPhotos.summary.title, "2 guided scan photos selected")
    try expectContains(twoPhotos.summary.detail, "front.jpg")
}

private func testCaptureMediaSelectionClearsWhenModeChanges() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )

    let changed = selection.changingMode(to: .manualUpload)

    try expectEqual(changed.mode, .manualUpload)
    try expectEqual(changed.media.count, 0)
    try expectFalse(changed.isReadyForUpload)
}

private func testCameraCaptureMediaBuilderBuildsReadySinglePhotoSelection() throws {
    let jpegData = Data([0xff, 0xd8, 0xff, 0xd9])

    let selection = CameraCaptureMediaBuilder.singlePhotoSelection(jpegData: jpegData)
    let payload = try selection.captureDraft(
        label: "silver spoon",
        materialsText: "metal",
        visualNotes: "bright reflection",
        source: "phone_camera"
    ).validatedUploadPayload()

    try expectEqual(selection.mode, .singlePhoto)
    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.media.count, 1)
    try expectEqual(selection.media[0].kind, .image)
    try expectEqual(selection.media[0].contentType, "image/jpeg")
    try expectEqual(selection.media[0].originalFilename, "camera-capture.jpg")
    try expectEqual(payload.metadata.captureMode, "single_photo")
    try expectEqual(payload.uploads[0].filename, "camera-capture.jpg")
    try expectEqual(payload.uploads[0].contentType, "image/jpeg")
    try expectEqual(payload.uploads[0].data, jpegData)
}

private func testGuidedScanPhotoSetBuilderBuildsSortedImageDrafts() throws {
    let media = try GuidedScanPhotoSetBuilder.mediaDrafts(
        from: [
            guidedScanImage(filename: "scan_003.heic", contentType: "image/heic"),
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(filename: "scan_002.png", contentType: "image/png"),
        ]
    )

    try expectEqual(media.map(\.originalFilename), ["scan_001.jpg", "scan_002.png", "scan_003.heic"])
    try expectEqual(media.map(\.contentType), ["image/jpeg", "image/png", "image/heic"])
    try expectTrue(media.allSatisfy { $0.kind == .image })
}

private func testGuidedScanPhotoSetBuilderTruncatesToTwelveImages() throws {
    let images = (0..<14).map { index in
        guidedScanImage(filename: String(format: "scan_%02d.jpg", index), contentType: "image/jpeg")
    }

    let media = try GuidedScanPhotoSetBuilder.mediaDrafts(from: images)

    try expectEqual(media.count, 12)
    try expectEqual(media.first?.originalFilename, "scan_00.jpg")
    try expectEqual(media.last?.originalFilename, "scan_11.jpg")
}

private func testGuidedScanPhotoSetBuilderRejectsTooFewImages() throws {
    try expectGuidedScanPhotoSetBuilderError(
        [guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg")],
        .tooFewImages(1)
    )
}

private func testGuidedScanPhotoSetBuilderRejectsUnsupportedContentType() throws {
    try expectGuidedScanPhotoSetBuilderError(
        [
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(filename: "scan_002.gif", contentType: "image/gif"),
        ],
        .unsupportedContentType("image/gif")
    )
}

private func testGuidedScanPhotoSetBuilderRejectsOversizedMedia() throws {
    let oversizedBytes = CaptureDraft.maxFileBytes + 1
    try expectGuidedScanPhotoSetBuilderError(
        [
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(
                filename: "scan_002.jpg",
                contentType: "image/jpeg",
                data: Data(repeating: 0, count: oversizedBytes)
            ),
        ],
        .mediaTooLarge(oversizedBytes, CaptureDraft.maxFileBytes)
    )
}

private func testARKitScanPackageBuilderBuildsReadySelection() throws {
    let selection = try ARKitScanPackageBuilder.selection(
        scanExport: ARKitScanExportFile(
            filename: "scan.glb",
            contentType: "model/gltf-binary",
            data: Data([1, 2, 3])
        ),
        referenceImages: [
            ARKitScanReferenceImageFile(filename: "b.jpg", contentType: "image/jpeg", data: Data([4])),
            ARKitScanReferenceImageFile(filename: "a.png", contentType: "image/png", data: Data([5])),
        ]
    )

    try expectEqual(selection.mode, .arkitScan)
    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.media.count, 3)
    try expectEqual(selection.media[0].kind, .scanAsset)
    try expectEqual(selection.media[0].originalFilename, "scan.glb")
    try expectEqual(selection.media[1].originalFilename, "a.png")
    try expectEqual(selection.media[2].originalFilename, "b.jpg")
}

private func testARKitScanPackageBuilderNormalizesAndSortsReferences() throws {
    let selection = try ARKitScanPackageBuilder.selection(
        scanExport: ARKitScanExportFile(
            filename: "scan.usdz",
            contentType: " MODEL/VND.USDZ+ZIP ",
            data: Data([1])
        ),
        referenceImages: [
            ARKitScanReferenceImageFile(
                filename: "reference_10.HEIC",
                contentType: " IMAGE/HEIC ",
                data: Data([2])
            ),
            ARKitScanReferenceImageFile(
                filename: "reference_02.jpg",
                contentType: " IMAGE/JPEG ",
                data: Data([3])
            ),
        ]
    )

    try expectEqual(selection.media[0].contentType, "model/vnd.usdz+zip")
    try expectEqual(selection.media[1].contentType, "image/jpeg")
    try expectEqual(selection.media[2].contentType, "image/heic")
}

private func testARKitScanPackageBuilderTruncatesReferencesToEleven() throws {
    let references = (0..<14).map { index in
        ARKitScanReferenceImageFile(
            filename: String(format: "ref_%02d.jpg", index),
            contentType: "image/jpeg",
            data: Data([UInt8(index)])
        )
    }

    let selection = try ARKitScanPackageBuilder.selection(
        scanExport: ARKitScanExportFile(
            filename: "scan.bin",
            contentType: "application/octet-stream",
            data: Data([1])
        ),
        referenceImages: references
    )

    try expectEqual(selection.media.count, 12)
    try expectEqual(selection.media.filter { $0.kind == .image }.count, 11)
    try expectEqual(selection.media[0].kind, .scanAsset)
}

private func testARKitScanPackageBuilderRejectsUnsupportedScan() throws {
    try expectThrows(ARKitScanPackageBuilderError.unsupportedScanContentType("model/obj")) {
        _ = try ARKitScanPackageBuilder.selection(
            scanExport: ARKitScanExportFile(
                filename: "scan.obj",
                contentType: "model/obj",
                data: Data([1])
            ),
            referenceImages: []
        )
    }
}

private func testARKitScanPackageBuilderRejectsUnsupportedReference() throws {
    try expectThrows(ARKitScanPackageBuilderError.unsupportedReferenceContentType("image/gif")) {
        _ = try ARKitScanPackageBuilder.selection(
            scanExport: ARKitScanExportFile(
                filename: "scan.glb",
                contentType: "model/gltf-binary",
                data: Data([1])
            ),
            referenceImages: [
                ARKitScanReferenceImageFile(filename: "ref.gif", contentType: "image/gif", data: Data([2])),
            ]
        )
    }
}

private func testARKitScanPackageBuilderRejectsOversizedScan() throws {
    let oversizedBytes = CaptureDraft.maxFileBytes + 1

    try expectThrows(ARKitScanPackageBuilderError.scanTooLarge(oversizedBytes, CaptureDraft.maxFileBytes)) {
        _ = try ARKitScanPackageBuilder.selection(
            scanExport: ARKitScanExportFile(
                filename: "scan.glb",
                contentType: "model/gltf-binary",
                data: Data(repeating: 1, count: oversizedBytes)
            ),
            referenceImages: []
        )
    }
}

private func testARKitScanPackageBuilderRejectsOversizedReference() throws {
    let oversizedBytes = CaptureDraft.maxFileBytes + 1

    try expectThrows(
        ARKitScanPackageBuilderError.referenceTooLarge(
            "ref.jpg",
            oversizedBytes,
            CaptureDraft.maxFileBytes
        )
    ) {
        _ = try ARKitScanPackageBuilder.selection(
            scanExport: ARKitScanExportFile(
                filename: "scan.glb",
                contentType: "model/gltf-binary",
                data: Data([1])
            ),
            referenceImages: [
                ARKitScanReferenceImageFile(
                    filename: "ref.jpg",
                    contentType: "image/jpeg",
                    data: Data(repeating: 1, count: oversizedBytes)
                ),
            ]
        )
    }
}

private func testCaptureGenerationReadinessWaitsForGuidedScanPhotos() throws {
    let selection = CaptureMediaSelection(
        mode: .guidedScan,
        media: [
            captureMedia(filename: "scan_001.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )

    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(readiness.status, .waiting)
    try expectEqual(readiness.route, .waiting)
    try expectEqual(readiness.title, "Guided scan needs photos")
    try expectContains(readiness.detail, "2 photos")
}

private func testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute() throws {
    let selection = CaptureMediaSelection(
        mode: .guidedScan,
        media: (0..<6).map { index in
            captureMedia(filename: "scan_\(index).jpg", contentType: "image/jpeg", kind: .image)
        }
    )

    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(readiness.status, .ready)
    try expectEqual(readiness.route, .multiImage)
    try expectEqual(readiness.route.displayLabel, "multi_image")
    try expectEqual(readiness.sourceCount, 6)
    try expectEqual(readiness.selectedProviderSourceCount, 4)
    try expectEqual(readiness.title, "Guided scan ready for 3D")
    try expectContains(readiness.detail, "6 photos")
    try expectContains(readiness.detail, "Meshy")
}

private func testCaptureGenerationReadinessMarksARKitScanAssetRoute() throws {
    let selection = try ARKitScanPackageBuilder.selection(
        scanExport: ARKitScanExportFile(
            filename: "idol.glb",
            contentType: "model/gltf-binary",
            data: Data([1])
        ),
        referenceImages: [
            ARKitScanReferenceImageFile(filename: "front.jpg", contentType: "image/jpeg", data: Data([2])),
            ARKitScanReferenceImageFile(filename: "side.png", contentType: "image/png", data: Data([3])),
        ]
    )

    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: realThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(readiness.status, .ready)
    try expectEqual(readiness.route, .scanAsset)
    try expectEqual(readiness.route.displayLabel, "scan_asset")
    try expectEqual(readiness.sourceCount, 3)
    try expectEqual(readiness.selectedProviderSourceCount, 1)
    try expectEqual(readiness.title, "Scan package ready for 3D")
    try expectContains(readiness.detail, "1 scan asset + 2 references")
    try expectContains(readiness.detail, "Real 3D provider ready")
}

private func testCaptureGenerationReadinessMarksMissingThreeDProvider() throws {
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: readyGuidedScanSelection(),
        providerReadiness: missingThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(readiness.status, .needsAttention)
    try expectEqual(readiness.route, .multiImage)
    try expectContains(readiness.detail, "MESHY_API_KEY")
}

private func testCaptureGenerationReadinessRedactsProviderErrors() throws {
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: readyGuidedScanSelection(),
        providerReadiness: nil,
        providerReadinessError: "sk-secret /Users/zhexu/private"
    )

    try expectEqual(readiness.status, .needsAttention)
    try expectEqual(readiness.detail, "[withheld]")
}

private func testThreeDGenerationInputReviewWaitsForCaptureMedia() throws {
    let selection = CaptureMediaSelection(mode: .guidedScan)
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    let review = ThreeDGenerationInputReviewBuilder.build(
        selection: selection,
        generationReadiness: readiness,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(review.status, .waiting)
    try expectEqual(review.canForge3D, false)
    try expectEqual(review.routeLabel, "waiting")
    try expectContains(review.title, "3D input waiting")
    try expectContains(review.row(id: "capture_mode")?.detail ?? "", "guided_scan")
    try expectContains(review.row(id: "provider_route")?.detail ?? "", "waiting")
}

private func testThreeDGenerationInputReviewShowsGuidedScanProviderSelection() throws {
    let selection = CaptureMediaSelection(
        mode: .guidedScan,
        media: (0..<9).map { index in
            captureMedia(filename: "scan_\(index).jpg", contentType: "image/jpeg", kind: .image)
        }
    )
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )

    let review = ThreeDGenerationInputReviewBuilder.build(
        selection: selection,
        generationReadiness: readiness,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )
    let text = String(decoding: try PMFJSON.encoder.encode(review), as: UTF8.self)

    try expectEqual(review.status, .ready)
    try expectEqual(review.canForge3D, true)
    try expectEqual(review.routeLabel, "multi_image")
    try expectEqual(review.selectedProviderSourceCount, 4)
    try expectContains(review.row(id: "source_media")?.detail ?? "", "9 guided scan photos")
    try expectContains(review.row(id: "provider_route")?.detail ?? "", "selected 4/9 provider images")
    try expectContains(review.row(id: "provider")?.detail ?? "", "Local demo route ready")
    try expectContains(review.privacyNotes.joined(separator: " "), "Raw capture files withheld")
    try expectNotContains(text, "scan_0.jpg")
}

private func testThreeDGenerationInputReviewShowsARKitScanPackage() throws {
    let selection = try ARKitScanPackageBuilder.selection(
        scanExport: ARKitScanExportFile(
            filename: "idol.glb",
            contentType: "model/gltf-binary",
            data: Data([1])
        ),
        referenceImages: [
            ARKitScanReferenceImageFile(filename: "front.jpg", contentType: "image/jpeg", data: Data([2])),
            ARKitScanReferenceImageFile(filename: "side.png", contentType: "image/png", data: Data([3])),
        ]
    )
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: realThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    let review = ThreeDGenerationInputReviewBuilder.build(
        selection: selection,
        generationReadiness: readiness,
        providerReadiness: realThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(review.status, .ready)
    try expectEqual(review.routeLabel, "scan_asset")
    try expectEqual(review.selectedProviderSourceCount, 1)
    try expectContains(review.row(id: "source_media")?.detail ?? "", "1 scan asset + 2 references")
    try expectContains(review.row(id: "provider_route")?.detail ?? "", "scan asset handoff")
    try expectContains(review.row(id: "provider")?.detail ?? "", "Meshy real provider ready")
}

private func testThreeDGenerationInputReviewShowsMeshyReadyRoute() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: realThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    let review = ThreeDGenerationInputReviewBuilder.build(
        selection: selection,
        generationReadiness: readiness,
        providerReadiness: realThreeDProviderReadiness(),
        providerReadinessError: nil
    )

    try expectEqual(review.status, .ready)
    try expectEqual(review.routeLabel, "single_image")
    try expectEqual(review.selectedProviderSourceCount, 1)
    try expectEqual(review.canForge3D, true)
    try expectContains(review.title, "3D input ready")
    try expectContains(review.detail, "Real 3D provider ready")
    try expectContains(review.row(id: "provider_route")?.detail ?? "", "image-to-3D")
    try expectContains(review.row(id: "provider")?.detail ?? "", "Meshy real provider ready")
}

private func testThreeDGenerationInputReviewRedactsUnsafeText() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "/Users/zhexu/secret.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let unsafeError = "Authorization=Bearer secret sk-test /Users/zhexu/private file:///tmp/private local-capture://cap data:image/png;base64,AAAA checkout_url=https://pay.example api_key=secret"
    let readiness = CaptureGenerationReadinessBuilder.build(
        selection: selection,
        providerReadiness: nil,
        providerReadinessError: unsafeError
    )

    let review = ThreeDGenerationInputReviewBuilder.build(
        selection: selection,
        generationReadiness: readiness,
        providerReadiness: nil,
        providerReadinessError: unsafeError
    )
    let text = String(decoding: try PMFJSON.encoder.encode(review), as: UTF8.self)

    try expectEqual(review.status, .needsAttention)
    try expectEqual(review.canForge3D, false)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "data:image")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key=secret")
    try expectNotContains(text, "secret.jpg")
}

private func testCaptureGenerationReceiptWaitsBeforeCapture() throws {
    let receipt = CaptureGenerationReceiptBuilder.build(
        capture: nil,
        session: nil,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )

    try expectEqual(receipt.status, .waiting)
    try expectContains(receipt.title, "Capture waiting")
    try expectContains(receipt.detail, "Guided scan ready")
    try expectContains(receipt.rows.joined(separator: " "), "multi_image")
}

private func testCaptureGenerationReceiptShowsUploadedCaptureBeforeSession() throws {
    let receipt = CaptureGenerationReceiptBuilder.build(
        capture: guidedScanObjectCapture(),
        session: nil,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let text = receipt.rows.joined(separator: " ")

    try expectEqual(receipt.status, .waiting)
    try expectContains(receipt.title, "Capture uploaded")
    try expectContains(text, "cap_ba02a3816bd145b4")
    try expectContains(text, "guided_scan")
    try expectContains(text, "reference_image 3")
    try expectContains(receipt.detail, "waiting for myth session")
}

private func testCaptureGenerationReceiptShowsReadyGuidedScanGeneration() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let receipt = CaptureGenerationReceiptBuilder.build(
        capture: guidedScanObjectCapture(),
        session: session,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let text = receipt.rows.joined(separator: " ")

    try expectEqual(receipt.status, .ready)
    try expectContains(receipt.title, "Capture-to-3D ready")
    try expectContains(text, "cap_ba02a3816bd145b4")
    try expectContains(text, "guided_scan")
    try expectContains(text, "provider local_stub")
    try expectContains(text, "input multi_image")
    try expectContains(text, "source images 3")
    try expectContains(text, "source assets 0")
    try expectContains(text, "selected 3/3")
    try expectContains(text, "/openapi/v1/multi-image-to-3d")
    try expectContains(receipt.privacyNotes.joined(separator: " "), "Raw capture media withheld")
}

private func testCaptureGenerationReceiptFlagsMissingProvenance() throws {
    var session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    session.generatedAsset.generationProvenance = nil

    let receipt = CaptureGenerationReceiptBuilder.build(
        capture: guidedScanObjectCapture(),
        session: session,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )

    try expectEqual(receipt.status, .needsAttention)
    try expectContains(receipt.title, "Capture-to-3D proof missing")
    try expectContains(receipt.detail, "Generation provenance has not loaded")
}

private func testCaptureGenerationReceiptRedactsUnsafeText() throws {
    var capture = guidedScanObjectCapture()
    capture.captureId = "cap_ba02a3816bd145b4 /Users/zhexu/private"
    capture.source = "local-capture://cap_ba02a3816bd145b4/media_0.jpg"
    capture.mediaItems[0].uri = "local-capture://cap_ba02a3816bd145b4/media_0.jpg"
    var session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    session.generatedAsset.provider = "sk-test"
    session.generatedAsset.generationProvenance = GeneratedAssetProvenance(
        inputMode: "multi_image",
        providerRoute: "Bearer secret /Users/zhexu/private file:///tmp/private local-capture://cap checkout_url=https://pay.example/private",
        sourceImageCount: 3,
        selectedSourceImageCount: 2,
        sourceAssetCount: 0,
        maxSourceImages: 4,
        selectionReason: "api_key=secret private_message: raw",
        rawSourcesIncluded: false
    )

    let receipt = CaptureGenerationReceiptBuilder.build(
        capture: capture,
        session: session,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let text = String(decoding: try PMFJSON.encoder.encode(receipt), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
    try expectNotContains(text, "private_message:")
}

private func testForgeProgressReceiptWaitsBeforeForge() throws {
    let receipt = ForgeProgressReceiptBuilder.build(
        state: ForgeFlowState(),
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let labels = receipt.rows.map(\.label).joined(separator: " ")
    let details = receipt.rows.map(\.detail).joined(separator: " ")

    try expectEqual(receipt.status, .waiting)
    try expectContains(receipt.title, "Forge waiting")
    try expectContains(labels, "Capture upload")
    try expectContains(details, "multi_image")
}

private func testForgeProgressReceiptShowsCaptureUploadRunning() throws {
    let state = ForgeFlowState(phase: .uploadingCapture)
    let receipt = ForgeProgressReceiptBuilder.build(
        state: state,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let statuses = receipt.rows.map(\.status).joined(separator: " ")
    let details = receipt.rows.map(\.detail).joined(separator: " ")

    try expectEqual(receipt.status, .running)
    try expectContains(receipt.title, "Forge running")
    try expectContains(statuses, "running")
    try expectContains(details, "Uploading capture")
}

private func testForgeProgressReceiptShowsMythSessionRunningAfterCaptureUpload() throws {
    let capture = guidedScanObjectCapture()
    let state = ForgeFlowState(phase: .creatingSession, capture: capture)
    let receipt = ForgeProgressReceiptBuilder.build(
        state: state,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let details = receipt.rows.map(\.detail).joined(separator: " ")

    try expectEqual(receipt.status, .running)
    try expectContains(receipt.detail, "Creating myth session")
    try expectContains(details, "cap_ba02a3816bd145b4")
}

private func testForgeProgressReceiptShowsReadyProviderAndNPCRuntime() throws {
    var state = ForgeFlowState()
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(session))

    let receipt = ForgeProgressReceiptBuilder.build(
        state: state,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let text = receipt.rows.map { "\($0.label) \($0.status) \($0.detail)" }.joined(separator: " ")

    try expectEqual(receipt.status, .ready)
    try expectContains(receipt.title, "Forge ready")
    try expectContains(text, "3D generation")
    try expectContains(text, "local_stub")
    try expectContains(text, "/openapi/v1/multi-image-to-3d")
    try expectContains(text, "NPC Agent")
    try expectContains(text, "local_agent_runtime")
}

private func testForgeProgressReceiptRedactsUnsafeFailure() throws {
    let error = ForgeFlowError.transport(
        "sk-secret Bearer token api_key=secret /Users/zhexu/private /tmp/private " +
            "file:///tmp/private local-capture://cap checkout_url=https://pay.example/private " +
            "private_message: raw"
    )
    let state = ForgeFlowState(phase: .failed(error))
    let receipt = ForgeProgressReceiptBuilder.build(
        state: state,
        captureGenerationReadiness: readyCaptureGenerationReadiness()
    )
    let text = String(decoding: try PMFJSON.encoder.encode(receipt), as: UTF8.self)

    try expectEqual(receipt.status, .needsAttention)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-secret")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "/tmp/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "private_message:")
}

private func testGenerationResultReceiptWaitsForForge() throws {
    let receipt = GenerationResultReceiptBuilder.build(session: nil)

    try expectEqual(receipt.status, .waiting)
    try expectEqual(receipt.canPresentResult, false)
    try expectContains(receipt.title, "Generation result waiting")
    try expectContains(receipt.detail, "Forge a myth session")
    try expectContains(receipt.row(id: "game_asset")?.detail ?? "", "No game asset")
}

private func testGenerationResultReceiptShowsCompleteForgeResult() throws {
    var session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "https://cdn.example.com/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "game_asset",
                    format: "glb",
                    uri: "https://cdn.example.com/relic.glb",
                    isSceneLoadable: false
                ),
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "dae",
                    uri: "https://cdn.example.com/relic.dae",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    session.generatedAsset.provider = "meshy"
    session.generatedAsset.generationProvenance = GeneratedAssetProvenance(
        inputMode: "multi_image",
        providerRoute: "/openapi/v1/multi-image-to-3d",
        sourceImageCount: 9,
        selectedSourceImageCount: 4,
        sourceAssetCount: 0,
        maxSourceImages: 4,
        selectionReason: "selected 4/9 guided scan sources",
        rawSourcesIncluded: false
    )
    session.printCandidate = PrintCandidate(
        kind: "print_asset",
        sourceAssetUri: "https://cdn.example.com/relic.glb",
        provider: "local",
        format: "3mf",
        uri: "local://print-candidates/relic.3mf",
        requiresUserApproval: true,
        approvalReason: "review before third-party print handoff",
        printabilityNotes: ["Base stabilized."]
    )
    session.npcAgentRuntime = "openai_structured_runtime"
    session.npcAgentTraces = [
        sampleNPCAgentTrace(npcId: "mara"),
        sampleNPCAgentTrace(npcId: "ior"),
        sampleNPCAgentTrace(npcId: "senn"),
    ]

    let receipt = GenerationResultReceiptBuilder.build(session: session)

    try expectEqual(receipt.status, .ready)
    try expectEqual(receipt.canPresentResult, true)
    try expectContains(receipt.title, "Generation result ready")
    try expectContains(receipt.detail, "myth_test")
    try expectContains(receipt.row(id: "game_asset")?.detail ?? "", "meshy glb")
    try expectContains(receipt.row(id: "game_asset")?.detail ?? "", "multi_image")
    try expectContains(receipt.row(id: "ios_scene")?.detail ?? "", "dae scene-loadable")
    try expectContains(receipt.row(id: "print_candidate")?.detail ?? "", "3mf")
    try expectContains(receipt.row(id: "print_candidate")?.detail ?? "", "approval required")
    try expectContains(receipt.row(id: "npc_agent")?.detail ?? "", "openai_structured_runtime")
    try expectContains(receipt.row(id: "npc_agent")?.detail ?? "", "3 traces")
    try expectContains(receipt.privacyNotes.joined(separator: " "), "Raw provider URIs and prompts withheld")
}

private func testGenerationResultReceiptRequiresIOSSceneVariant() throws {
    var session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "https://cdn.example.com/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "game_asset",
                    format: "glb",
                    uri: "https://cdn.example.com/relic.glb",
                    isSceneLoadable: false
                ),
            ]
        )
    )
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]

    let receipt = GenerationResultReceiptBuilder.build(session: session)

    try expectEqual(receipt.status, .needsAttention)
    try expectEqual(receipt.canPresentResult, false)
    try expectContains(receipt.title, "Generation result needs attention")
    try expectContains(receipt.row(id: "ios_scene")?.detail ?? "", "missing scene-loadable iOS asset")
}

private func testGenerationResultReceiptRedactsUnsafeText() throws {
    var session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "file:///Users/zhexu/private/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "dae",
                    uri: "local-capture://cap/private.dae",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    session.sessionId = "myth_test sk-test"
    session.generatedAsset.provider = "Bearer provider-token"
    session.generatedAsset.prompt = "secret prompt /Users/zhexu/photo.jpg data:image/png;base64,AAAA api_key=secret"
    session.generatedAsset.generationProvenance = GeneratedAssetProvenance(
        inputMode: "single_image",
        providerRoute: "checkout_url=https://pay.example/relic",
        sourceImageCount: 1,
        selectedSourceImageCount: 1,
        sourceAssetCount: 0,
        maxSourceImages: 4,
        selectionReason: "file:///tmp/private local-capture://cap",
        rawSourcesIncluded: false
    )
    session.printCandidate = PrintCandidate(
        kind: "print_asset",
        sourceAssetUri: "file:///tmp/private.glb",
        provider: "local",
        format: "stl",
        uri: "https://checkout.example.com/order",
        requiresUserApproval: true,
        approvalReason: "payment_link https://pay.example sk-test",
        printabilityNotes: ["private /Users/zhexu"]
    )
    session.npcAgentRuntime = "openai Bearer runtime-token"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]

    let receipt = GenerationResultReceiptBuilder.build(session: session)
    let text = String(decoding: try PMFJSON.encoder.encode(receipt), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "data:image")
    try expectNotContains(text, "checkout")
    try expectNotContains(text, "pay.example")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "api_key=secret")
    try expectNotContains(text, "payment_link")
}

private func testForgeFlowReducerTransitionsThroughReadyAndReset() throws {
    let metadata = sampleMetadata()
    let context = sampleContext()
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    var state = ForgeFlowState()
    state = ForgeFlowReducer.reduce(state: state, event: .setObjectMetadata(metadata))
    try expectEqual(state.phase, .editingObject)
    try expectEqual(state.metadata, metadata)

    state = ForgeFlowReducer.reduce(state: state, event: .setContextCapsule(context))
    try expectEqual(state.phase, .editingObject)
    try expectEqual(state.context, context)

    state = ForgeFlowReducer.reduce(state: state, event: .beginUpload)
    try expectEqual(state.phase, .uploadingCapture)

    state = ForgeFlowReducer.reduce(state: state, event: .captureUploaded(capture))
    try expectEqual(state.phase, .creatingSession)
    try expectEqual(state.capture, capture)

    state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(session))
    try expectEqual(state.phase, .ready(session))

    state = ForgeFlowReducer.reduce(state: state, event: .requestFailed(.httpStatus(500, "redacted")))
    try expectEqual(state.phase, .failed(.httpStatus(500, "redacted")))

    state = ForgeFlowReducer.reduce(state: state, event: .reset)
    try expectEqual(state.phase, .idle)
    try expectTrue(state.metadata == nil)
    try expectTrue(state.context == nil)
    try expectTrue(state.capture == nil)
}

private func testForgeFlowServiceUploadsCaptureThenCreatesSession() async throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(uploadResult: .success(capture), sessionResult: .success(session))
    let service = ForgeFlowService(api: api)
    let snapshots = SnapshotRecorder()

    let finalState = await service.forge(
        draft: sampleCaptureDraft(),
        context: sampleContext()
    ) { state in
        snapshots.append(state)
    }

    try expectEqual(finalState.phase, .ready(session))
    try expectEqual(api.uploadedMetadata, sampleMetadata())
    try expectEqual(api.uploadedMedia.map(\.contentType), ["image/jpeg"])
    try expectEqual(api.sessionCaptureIds, ["cap_ba02a3816bd145b4"])
    try expectEqual(api.sessionContexts, [sampleContext()])
    try expectEqual(snapshots.values.map(\.phase), [
        .editingObject,
        .editingObject,
        .uploadingCapture,
        .creatingSession,
        .ready(session),
    ])
}

private func testForgeFlowServiceStopsBeforeSessionWhenUploadFails() async throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(
        uploadResult: .failure(ForgeFlowError.httpStatus(413, "too large")),
        sessionResult: .success(session)
    )
    let service = ForgeFlowService(api: api)
    let snapshots = SnapshotRecorder()

    let finalState = await service.forge(
        draft: sampleCaptureDraft(),
        context: sampleContext()
    ) { state in
        snapshots.append(state)
    }

    try expectEqual(finalState.phase, .failed(.httpStatus(413, "too large")))
    try expectEqual(api.uploadedMedia.count, 1)
    try expectEqual(api.sessionCaptureIds, [])
    try expectEqual(snapshots.values.map(\.phase), [
        .editingObject,
        .editingObject,
        .uploadingCapture,
        .failed(.httpStatus(413, "too large")),
    ])
}

private func testForgeFlowServiceRejectsInvalidDraftBeforeNetwork() async throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(uploadResult: .success(capture), sessionResult: .success(session))
    let service = ForgeFlowService(api: api)

    let finalState = await service.forge(
        draft: CaptureDraft(
            label: " ",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        context: sampleContext()
    )

    try expectEqual(api.uploadedMedia.count, 0)
    try expectEqual(api.sessionCaptureIds, [])
    if case let .failed(.invalidCaptureDraft(message)) = finalState.phase {
        try expectContains(message, "missingLabel")
    } else {
        throw ContractTestError.expectationFailed("Expected invalid capture draft failure, got \(finalState.phase)")
    }
}

private func testSwiftUIScaffoldIncludesWorldResolution() throws {
    let appRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        .appendingPathComponent("apps/mobile/ios/App")
    let rootView = try sourceFile("ForgeRootView.swift", in: appRoot)
    let worldView = try sourceFile("WorldResolutionView.swift", in: appRoot)

    try expectContains(rootView, "WorldResolutionView(session: readySession)")
    try expectContains(worldView, "session.worldResolution")
    try expectContains(worldView, "acceptedActions")
    try expectContains(worldView, "rejectedActions")
    try expectContains(worldView, "visibleChanges")
}

private func testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
        )
    )

    try expectEqual(state.title, "The Key That Remembered")
    try expectEqual(state.providerLabel, "meshy")
    try expectEqual(state.formatLabel, "GLB")
    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.statusTitle, "Generated 3D asset ready")
    try expectContains(state.statusDetail, "download/import step")
}

private func testArtifactGenerationProvenanceSummaryShowsMultiImageRoute() throws {
    let summary = ArtifactGenerationProvenanceSummaryBuilder.build(
        provenance: GeneratedAssetProvenance(
            inputMode: "multi_image",
            providerRoute: "/openapi/v1/multi-image-to-3d",
            sourceImageCount: 4,
            selectedSourceImageCount: 3,
            sourceAssetCount: 0,
            maxSourceImages: 4,
            selectionReason: "Provider selected prepared guided-scan references.",
            rawSourcesIncluded: false
        )
    )

    try expectTrue(summary.isAvailable)
    try expectEqual(summary.title, "3D generation route")
    try expectEqual(summary.routeLabel, "Multi Image")
    try expectEqual(summary.sourceSummary, "3/4 images selected, max 4")
    try expectEqual(summary.providerRoute, "/openapi/v1/multi-image-to-3d")
    try expectEqual(summary.selectionReason, "Provider selected prepared guided-scan references.")
    try expectEqual(summary.privacySummary, "Raw source media withheld")
}

private func testArtifactGenerationProvenanceSummaryShowsScanAssets() throws {
    let summary = ArtifactGenerationProvenanceSummaryBuilder.build(
        provenance: GeneratedAssetProvenance(
            inputMode: "multi_image",
            providerRoute: "local_stub",
            sourceImageCount: 2,
            selectedSourceImageCount: 2,
            sourceAssetCount: 1,
            maxSourceImages: nil,
            selectionReason: "ARKit scan asset plus references.",
            rawSourcesIncluded: false
        )
    )

    try expectEqual(summary.sourceSummary, "2/2 images selected, 1 scan asset")
    try expectEqual(summary.providerRoute, "local_stub")
}

private func testArtifactGenerationProvenanceSummaryWaitsForMissingProvenance() throws {
    let summary = ArtifactGenerationProvenanceSummaryBuilder.build(provenance: nil)

    try expectFalse(summary.isAvailable)
    try expectEqual(summary.routeLabel, "Waiting")
    try expectContains(summary.sourceSummary, "generation provenance has not loaded")
}

private func testArtifactGenerationProvenanceSummaryRedactsUnsafeText() throws {
    let summary = ArtifactGenerationProvenanceSummaryBuilder.build(
        provenance: GeneratedAssetProvenance(
            inputMode: "single_image",
            providerRoute: "Bearer sk-test /Users/zhexu/private file:///tmp/private local-capture://cap",
            sourceImageCount: 1,
            selectedSourceImageCount: 1,
            sourceAssetCount: 0,
            maxSourceImages: nil,
            selectionReason: "api_key=secret checkout_url=https://pay.example/private",
            rawSourcesIncluded: true
        )
    )
    let text = String(decoding: try PMFJSON.encoder.encode(summary), as: UTF8.self)

    try expectContains(text, "[withheld]")
    try expectEqual(summary.privacySummary, "Raw source media retained")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "local-capture://")
    try expectNotContains(text, "api_key")
    try expectNotContains(text, "checkout_url")
}

private func testArtifactPreviewStateMarksLocalUSDZAsSceneLoadable() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "usdz", uri: "file:///tmp/relic.usdz")
        )
    )

    try expectTrue(state.isSceneLoadable)
    try expectEqual(state.statusTitle, "Local scene asset ready")
    try expectContains(state.statusDetail, "SceneKit")
}

private func testArtifactPreviewStateHandlesMissingURI() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "", uri: "")
        )
    )

    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.formatLabel, "Unknown")
    try expectEqual(state.statusTitle, "Awaiting 3D asset")
}

private func testArtifactPreviewStateHandlesMissingFormat() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "", uri: "https://cdn.example.com/relic")
        )
    )

    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.formatLabel, "Unknown")
    try expectEqual(state.statusTitle, "Awaiting 3D asset format")
    try expectContains(state.statusDetail, "format")
}

private func testArtifactAssetPreparerUsesLocalSceneURL() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "file:///tmp/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .localSceneReady)
    try expectEqual(prepared.sceneURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(prepared.cachedURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerDownloadsRemoteUSDZForSceneKit() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("usdz-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedSceneReady)
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"))
    try expectEqual(prepared.sceneURL, prepared.cachedURL)
    try expectEqual(await downloader.requestedURLs(), [URL(string: "https://cdn.example.com/relic.usdz")!])
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.usdz"])
    try expectEqual(await cache.storedData(), [Data("usdz-bytes".utf8)])
}

private func testArtifactAssetPreparerDownloadsRemoteDAEForLocalBackendScene() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("<COLLADA></COLLADA>".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "dae", uri: "http://192.168.1.10:8080/v1/generated-assets/myth_test/scene.dae")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedSceneReady)
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.dae"))
    try expectEqual(prepared.sceneURL, prepared.cachedURL)
    try expectEqual(
        await downloader.requestedURLs(),
        [URL(string: "http://192.168.1.10:8080/v1/generated-assets/myth_test/scene.dae")!]
    )
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.dae"])
    try expectEqual(await cache.storedData(), [Data("<COLLADA></COLLADA>".utf8)])
}

private func testArtifactAssetPreparerCachesRemoteGLBButRequiresConversion() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("glb-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedRequiresConversion)
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.glb"))
    try expectEqual(prepared.sceneURL, nil)
    try expectContains(prepared.statusDetail, "conversion")
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.glb"])
}

private func testArtifactAssetPreparerPrefersSceneVariantOverPrimaryGLB() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("usdz-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "https://cdn.example.com/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "game_asset",
                    format: "glb",
                    uri: "https://cdn.example.com/relic.glb",
                    isSceneLoadable: false
                ),
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "usdz",
                    uri: "https://cdn.example.com/relic.usdz",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedSceneReady)
    try expectEqual(prepared.sourceURI, "https://cdn.example.com/relic.usdz")
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"))
    try expectEqual(prepared.sceneURL, prepared.cachedURL)
    try expectEqual(await downloader.requestedURLs(), [URL(string: "https://cdn.example.com/relic.usdz")!])
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.usdz"])
    try expectEqual(await cache.storedData(), [Data("usdz-bytes".utf8)])
}

private func testArtifactAssetPreparerReportsLocalSceneVariantSourceURI() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "file:///tmp/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "usdz",
                    uri: "file:///tmp/relic.usdz",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .localSceneReady)
    try expectEqual(prepared.sourceURI, "file:///tmp/relic.usdz")
    try expectEqual(prepared.cachedURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(prepared.sceneURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerRejectsInvalidRemoteURI() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "not-a-remote-uri")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .unsupportedURI)
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerSkipsDownloadWhenFormatMissing() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "", uri: "https://cdn.example.com/relic")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .awaitingFormat)
    try expectEqual(prepared.statusTitle, "Awaiting 3D asset format")
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerTreatsCancellationAsCancelled() async throws {
    let downloader = RecordingArtifactAssetDownloader(error: CancellationError())
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cancelled)
    try expectEqual(prepared.statusTitle, "Asset preparation cancelled")
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactSceneLoadProofWaitsForPreparedAsset() throws {
    let proof = ArtifactSceneLoadProofBuilder.build(preparedAsset: nil, sceneLoadError: nil)

    try expectEqual(proof.status, .waiting)
    try expectFalse(proof.canOpenScene)
    try expectContains(proof.detail, "preparing")
}

private func testArtifactSceneLoadProofMarksLoadedScene() throws {
    let asset = generatedAsset(format: "dae", uri: "https://cdn.example.com/relic.dae")
    let proof = ArtifactSceneLoadProofBuilder.build(
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .cachedSceneReady,
            cachedURL: URL(fileURLWithPath: "/tmp/pmf-assets/relic.dae"),
            sceneURL: URL(fileURLWithPath: "/tmp/pmf-assets/relic.dae"),
            statusTitle: "Cached SceneKit asset ready",
            statusDetail: "SceneKit file cached."
        ),
        sceneLoadError: nil
    )

    try expectEqual(proof.status, .loaded)
    try expectTrue(proof.canOpenScene)
    try expectContains(proof.title, "Loaded")
}

private func testArtifactSceneLoadProofMarksConversionRequired() throws {
    let asset = generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
    let proof = ArtifactSceneLoadProofBuilder.build(
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .cachedRequiresConversion,
            cachedURL: URL(fileURLWithPath: "/tmp/pmf-assets/relic.glb"),
            sceneURL: nil,
            statusTitle: "Cached asset needs conversion",
            statusDetail: "GLB cached."
        ),
        sceneLoadError: nil
    )

    try expectEqual(proof.status, .conversionRequired)
    try expectFalse(proof.canOpenScene)
}

private func testArtifactSceneLoadProofRedactsFailedSceneLoad() throws {
    let asset = generatedAsset(format: "dae", uri: "https://cdn.example.com/relic.dae")
    let proof = ArtifactSceneLoadProofBuilder.build(
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .sceneLoadFailed,
            cachedURL: URL(fileURLWithPath: "/Users/zhexu/private/relic.dae"),
            sceneURL: nil,
            statusTitle: "SceneKit load failed sk-test",
            statusDetail: "Failed at file:///Users/zhexu/private/relic.dae"
        ),
        sceneLoadError: "Authorization Bearer sk-test file:///Users/zhexu/private/relic.dae"
    )
    let text = String(decoding: try PMFJSON.encoder.encode(proof), as: UTF8.self)

    try expectEqual(proof.status, .failed)
    try expectFalse(proof.canOpenScene)
    try expectContains(text, "[withheld]")
    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "file:///")
    try expectNotContains(text, "/Users/")
}

private func testArtifactHandoffActionsWaitForSession() throws {
    let summary = ArtifactHandoffActionBuilder.build(session: nil, preparedAsset: nil)

    try expectEqual(summary.title, "Forge an artifact first")
    try expectEqual(summary.canOpenScene, false)
    try expectEqual(summary.canShareCachedAsset, false)
    try expectEqual(summary.actions.count, 1)
    try expectEqual(summary.actions[0].kind, .waiting)
    try expectEqual(summary.actions[0].status, .waiting)
    try expectEqual(summary.actions[0].isEnabled, false)
}

private func testArtifactHandoffActionsOpenAndShareSceneAsset() throws {
    let asset = generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    let summary = ArtifactHandoffActionBuilder.build(
        session: mythSession(asset: asset),
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .cachedSceneReady,
            cachedURL: URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"),
            sceneURL: URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"),
            statusTitle: "Cached SceneKit asset ready",
            statusDetail: "The generated asset has been downloaded into the app cache."
        )
    )

    try expectEqual(summary.title, "SceneKit handoff ready")
    try expectEqual(summary.canOpenScene, true)
    try expectEqual(summary.canShareCachedAsset, true)
    try expectEqual(summary.actions.map(\.kind), [.openScene, .shareCachedAsset])
    try expectEqual(summary.actions[0].isPrimary, true)
    try expectEqual(summary.actions[0].isEnabled, true)
    try expectEqual(summary.actions[1].title, "Share Cached Asset")
    try expectContains(summary.actions[1].detail, "myth_test-meshy.usdz")
    try expectNotContains(summary.actions.map(\.detail).joined(separator: " "), "/tmp/")
}

private func testArtifactHandoffActionsShareCachedGLBNeedsConversion() throws {
    let asset = generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
    let summary = ArtifactHandoffActionBuilder.build(
        session: mythSession(asset: asset),
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .cachedRequiresConversion,
            cachedURL: URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.glb"),
            sceneURL: nil,
            statusTitle: "Cached asset needs conversion",
            statusDetail: "The generated GLB asset is cached locally."
        )
    )

    try expectEqual(summary.title, "Conversion required")
    try expectEqual(summary.canOpenScene, false)
    try expectEqual(summary.canShareCachedAsset, true)
    try expectEqual(summary.actions.map(\.kind), [.convertRequired, .shareCachedAsset])
    try expectEqual(summary.actions[0].status, .attention)
    try expectEqual(summary.actions[0].isEnabled, false)
    try expectContains(summary.actions[0].detail, "GLB/GLTF")
    try expectEqual(summary.actions[1].isEnabled, true)
}

private func testArtifactHandoffActionsOfferRetryAfterDownloadFailure() throws {
    let asset = generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    let summary = ArtifactHandoffActionBuilder.build(
        session: mythSession(asset: asset),
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .downloadFailed,
            cachedURL: nil,
            sceneURL: nil,
            statusTitle: "Generated asset download failed",
            statusDetail: "The app could not cache the generated asset."
        )
    )

    try expectEqual(summary.title, "Asset download failed")
    try expectEqual(summary.canOpenScene, false)
    try expectEqual(summary.canShareCachedAsset, false)
    try expectEqual(summary.actions.count, 1)
    try expectEqual(summary.actions[0].kind, .retryDownload)
    try expectEqual(summary.actions[0].title, "Retry Download")
    try expectEqual(summary.actions[0].isPrimary, true)
    try expectEqual(summary.actions[0].isEnabled, true)
}

private func testArtifactHandoffActionsOfferRetryAfterSceneLoadFailure() throws {
    let asset = generatedAsset(format: "dae", uri: "https://cdn.example.com/relic.dae")
    let summary = ArtifactHandoffActionBuilder.build(
        session: mythSession(asset: asset),
        preparedAsset: preparedArtifactAsset(
            asset: asset,
            status: .sceneLoadFailed,
            cachedURL: URL(fileURLWithPath: "/tmp/pmf-assets/relic.dae"),
            sceneURL: nil,
            statusTitle: "SceneKit load failed",
            statusDetail: "SceneKit could not parse the cached file."
        )
    )

    try expectEqual(summary.title, "SceneKit load failed")
    try expectEqual(summary.actions.map(\.kind), [.retryDownload])
    try expectEqual(summary.actions[0].isEnabled, true)
}

private func testArtifactHandoffActionsRedactUnsafeDetails() throws {
    let asset = generatedAsset(format: "usdz", uri: "https://checkout.example.com/sk-test/relic.usdz")
    let summary = ArtifactHandoffActionBuilder.build(
        session: mythSession(asset: asset),
        preparedAsset: PreparedArtifactAsset(
            preview: ArtifactPreviewState(asset: asset, title: "Bearer sk-test /Users/zhexu"),
            sourceURI: "Bearer sk-test /Users/zhexu checkout_url",
            cachedURL: URL(fileURLWithPath: "/Users/zhexu/pmf-assets/sk-test.usdz"),
            sceneURL: URL(fileURLWithPath: "/Users/zhexu/pmf-assets/sk-test.usdz"),
            status: .cachedSceneReady,
            statusTitle: "Cached SceneKit asset ready sk-test",
            statusDetail: "Authorization Bearer sk-test checkout_url /Users/zhexu"
        )
    )
    let text = ([summary.title, summary.detail] + summary.actions.flatMap { [$0.title, $0.detail] })
        .joined(separator: " ")

    try expectNotContains(text, "sk-test")
    try expectNotContains(text, "/Users/")
    try expectNotContains(text, "Bearer")
    try expectNotContains(text, "Authorization")
    try expectNotContains(text, "checkout_url")
}

private func sampleCaptureDraft() -> CaptureDraft {
    CaptureDraft(
        label: "old brass key",
        materialsText: "metal, brass",
        visualNotes: "worn teeth",
        source: "phone_capture",
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )
}

private func sampleMetadata() -> ObjectCaptureMetadata {
    ObjectCaptureMetadata(
        label: "old brass key",
        materials: ["metal", "brass"],
        source: "phone_capture",
        captureMode: "single_photo",
        visualNotes: "worn teeth"
    )
}

private func sampleContext() -> ContextCapsule {
    ContextCapsule(
        currentTheme: "deadline pressure",
        desiredTone: "tender, strange",
        recentMilestone: "finished a difficult project draft"
    )
}

private func samplePrintCandidate() -> PrintCandidate {
    PrintCandidate(
        kind: "print_asset",
        sourceAssetUri: "local://generated-assets/myth_test.glb",
        provider: "local_stub",
        format: "3mf",
        uri: "local://print-candidates/myth_test.3mf",
        requiresUserApproval: true,
        approvalReason: "review before fulfillment",
        printabilityNotes: ["stable base", "repair thin parts"]
    )
}

private func localPrintQuote() -> PrintQuote {
    PrintQuote(
        kind: "print_quote",
        provider: "local_stub",
        status: "draft_quote",
        sourceAssetUri: "local://generated-assets/myth_test.glb",
        printCandidateUri: "local://print-candidates/myth_test.3mf",
        currency: "USD",
        estimatedPriceCents: 1600,
        estimatedProductionDays: 5,
        estimatedShippingDays: 6,
        checkoutUrl: nil,
        requiresUserApproval: true,
        approvalReason: "review before fulfillment",
        quoteNotes: ["local quote stub"]
    )
}

private func showcaseEvidenceReadySession() -> MythSession {
    var session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "https://cdn.example.com/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "game_asset",
                    format: "glb",
                    uri: "https://cdn.example.com/relic.glb",
                    isSceneLoadable: false
                ),
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "dae",
                    uri: "https://cdn.example.com/relic.dae",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    session.generatedAsset.provider = "meshy"
    session.generatedAsset.generationProvenance = GeneratedAssetProvenance(
        inputMode: "multi_image",
        providerRoute: "/openapi/v1/multi-image-to-3d",
        sourceImageCount: 4,
        selectedSourceImageCount: 4,
        sourceAssetCount: 0,
        maxSourceImages: 4,
        selectionReason: "selected guided scan sources",
        rawSourcesIncluded: false
    )
    session.printCandidate = samplePrintCandidate()
    session.npcAgentRuntime = "openai_structured_runtime"
    session.npcAgentTraces = [
        sampleNPCAgentTrace(npcId: "mara"),
        sampleNPCAgentTrace(npcId: "ior"),
        sampleNPCAgentTrace(npcId: "senn"),
    ]
    return session
}

private func readyGuidedScanSelection() -> CaptureMediaSelection {
    CaptureMediaSelection(
        mode: .guidedScan,
        media: [
            captureMedia(filename: "scan_001.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "scan_002.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "scan_003.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )
}

private func guidedScanObjectCapture() -> ObjectCapture {
    ObjectCapture(
        captureId: "cap_ba02a3816bd145b4",
        status: "ready",
        source: "phone_capture",
        captureMode: "guided_scan",
        objectObservation: ObjectObservation(
            label: "old brass key",
            materials: ["metal", "brass"],
            source: "phone_capture",
            visualNotes: "worn teeth"
        ),
        mediaItems: [
            captureMediaItem(id: "media_0", role: "reference_image", contentType: "image/jpeg"),
            captureMediaItem(id: "media_1", role: "reference_image", contentType: "image/jpeg"),
            captureMediaItem(id: "media_2", role: "reference_image", contentType: "image/png"),
        ],
        createdAt: "2026-06-05T00:00:00+00:00"
    )
}

private func captureMediaItem(
    id: String,
    role: String,
    contentType: String,
    byteSize: Int = 9
) -> CaptureMediaItem {
    CaptureMediaItem(
        mediaId: id,
        role: role,
        contentType: contentType,
        byteSize: byteSize,
        uri: "local-capture://cap_ba02a3816bd145b4/\(id).jpg",
        moderationStatus: "needs_review"
    )
}

private func readyCaptureGenerationReadiness(
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil
) -> CaptureGenerationReadiness {
    CaptureGenerationReadinessBuilder.build(
        selection: readyGuidedScanSelection(),
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError
    )
}

private func readyForgeReadinessSummary() -> ForgeReadinessSummary {
    ForgeReadinessSummaryBuilder.build(
        captureGenerationReadiness: readyCaptureGenerationReadiness(),
        contextCapsuleReview: approvedContextCapsuleReview(),
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil,
        npcAgentModeSummary: localDemoNPCAgentModeSummary()
    )
}

private func approvedContextCapsuleReview() -> ContextCapsuleReview {
    ContextCapsuleReviewBuilder.build(
        currentTheme: "deadline pressure",
        desiredTone: "tender, strange",
        isApproved: true
    )
}

private func localDemoNPCAgentModeSummary() -> NPCAgentModeSummary {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]
    return localDemoNPCAgentModeSummary(session: session)
}

private func localDemoNPCAgentModeSummary(session: MythSession) -> NPCAgentModeSummary {
    return NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: localDemoProviderReadiness(),
        providerReadinessError: nil
    )
}

private func missingOpenAINPCAgentModeSummary() -> NPCAgentModeSummary {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcDirector = "openai"
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]
    return missingOpenAINPCAgentModeSummary(session: session)
}

private func missingOpenAINPCAgentModeSummary(session: MythSession) -> NPCAgentModeSummary {
    return NPCAgentModeSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        providerReadiness: missingOpenAINPCProviderReadiness(),
        providerReadinessError: nil
    )
}

private func npcAgentTickSummary(
    session: MythSession,
    isAdvancingTick: Bool = false,
    isRunningAutonomy: Bool = false,
    errorMessage: String? = nil
) -> NPCAgentTickSummary {
    NPCAgentTickSummaryBuilder.build(
        session: session,
        latestTick: nil,
        tickHistoryCount: 0,
        isAdvancingTick: isAdvancingTick,
        isRunningAutonomy: isRunningAutonomy,
        errorMessage: errorMessage
    )
}

private func localAgentSession() -> MythSession {
    var session = mythSession(asset: generatedAsset(format: "glb", uri: "local://asset.glb"))
    session.npcAgentRuntime = "local_agent_runtime"
    session.npcAgentTraces = [sampleNPCAgentTrace(npcId: "mara")]
    return session
}

private func finalShowcaseSummary(
    session: MythSession? = nil,
    npcTickHistoryCount: Int = 0,
    printQuote: PrintQuote? = nil,
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil
) -> FinalShowcaseSummary {
    FinalShowcaseSummaryBuilder.build(
        captureSelection: readyGuidedScanSelection(),
        session: session,
        npcTickHistoryCount: npcTickHistoryCount,
        printQuote: printQuote,
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError
    )
}

private func devicePreflightSummary(
    backendBaseURL: URL,
    backendHealthProbe: BackendHealthProbe? = nil,
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil,
    finalDemoLaunch: FinalDemoLaunchReport? = readyDevicePreflightFinalDemoLaunchReport(),
    finalDemoLaunchError: String? = nil,
    finalShowcaseSummary: FinalShowcaseSummary = finalShowcaseSummary(),
    savedNPCTickCount: Int = 0
) -> DevicePreflightSummary {
    DevicePreflightSummaryBuilder.build(
        backendBaseURL: backendBaseURL,
        backendHealthProbe: backendHealthProbe,
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError,
        finalDemoLaunch: finalDemoLaunch,
        finalDemoLaunchError: finalDemoLaunchError,
        finalShowcaseSummary: finalShowcaseSummary,
        savedNPCTickCount: savedNPCTickCount
    )
}

private func readyDevicePreflightFinalDemoLaunchReport() -> FinalDemoLaunchReport {
    var report = finalDemoLaunchReport(
        overallStatus: "ready",
        finalOperatorHandoffStatus: "ready",
        iosDeployRunbookStatus: "ready",
        iosDeployRunbookSlotStatus: "ready",
        iosDeployRunbookThreeDSlotStatus: "ready",
        iosDeviceEvidenceStatus: "ready",
        iosDeviceEvidenceSlotStatus: "ready",
        iosDeviceLaunchRehearsalStatus: "ready",
        iosDeviceLaunchCertificateStatus: "ready",
        iosDeviceLaunchCertificateGateStatus: "ready"
    )
    report.finalResourceRequirements = readyFinalResourceRequirementsReport()
    report.finalResourceFillGuide = readyFinalResourceFillGuideReport()
    report.finalResourceApplyPreview = readyFinalResourceApplyPreviewReport()
    report.finalLaunchClosurePacket = readyFinalLaunchClosurePacket()
    return report
}

private func readyFinalClosurePacketReport() -> FinalDemoLaunchReport {
    var report = readyDevicePreflightFinalDemoLaunchReport()
    report.finalLaunchClosurePacket = readyFinalLaunchClosurePacket()
    return report
}

private func readyFinalLaunchClosurePacket() -> FinalLaunchClosurePacketReport {
    FinalLaunchClosurePacketReport(
        kind: "final_launch_closure_packet_report",
        status: "ready",
        summary: FinalLaunchClosurePacketSummary(
            sections: 6,
            actions: 8,
            ready: 8,
            missing: 0,
            blocked: 0,
            manual: 0,
            live: 0,
            partial: 0,
            optional: 0,
            requiredSections: 5,
            requiredActions: 8,
            secretActions: 0,
            requiresUserInput: 0,
            requiresUserConfirmation: 0,
            requiresCostConsent: 0,
            globalActions: 0,
            xcodeOrSigningActions: 0,
            safeLocalWrites: 0,
            liveProviderCalls: 0
        ),
        sections: [],
        sectionsById: [:],
        operatorActions: [],
        commands: ["make final-launch-closure-packet"],
        safety: FinalLaunchClosurePacketSafety(
            commandsRun: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            runsShellWriters: false,
            providerCalls: false,
            liveProviderCalls: false,
            globalMutation: false,
            xcodeOrSigning: false,
            keychainWrites: false,
            providerSecretsInReport: false,
            rawPrivateContextInReport: false,
            rawMediaInReport: false,
            paymentLinksInReport: false,
            localPathsInReport: false,
            describesGlobalActions: true,
            requiresCostConsentForLiveActions: false
        )
    )
}

private func blockedFinalResourceItemsJSON() -> String {
    """
    [
      {
        "id": "MESHY_API_KEY",
        "status": "missing",
        "required": true,
        "configured": false,
        "redacted": false,
        "classification": "missing_required_value"
      },
      {
        "id": "OPENAI_API_KEY",
        "status": "missing",
        "required": true,
        "configured": false,
        "redacted": false,
        "classification": "missing_required_value"
      },
      {
        "id": "PMF_BACKEND_BASE_URL",
        "status": "blocked",
        "required": true,
        "configured": false,
        "redacted": true,
        "classification": "loopback_url"
      }
    ]
    """
}

private func readyFinalResourceItemsJSON() -> String {
    """
    [
      {
        "id": "MESHY_API_KEY",
        "status": "ready",
        "required": true,
        "configured": true,
        "redacted": true
      },
      {
        "id": "OPENAI_API_KEY",
        "status": "ready",
        "required": true,
        "configured": true,
        "redacted": true
      },
      {
        "id": "PMF_BACKEND_BASE_URL",
        "status": "ready",
        "required": true,
        "configured": true,
        "redacted": true
      },
      {
        "id": "PRINT_PROVIDER",
        "status": "ready",
        "required": false,
        "configured": true,
        "redacted": false,
        "normalized_value": "local"
      }
    ]
    """
}

private func autoFinalResourceItemsJSON() -> String {
    """
    [
      {
        "id": "MESHY_API_KEY",
        "status": "ready",
        "required": true,
        "configured": true,
        "redacted": true
      },
      {
        "id": "PMF_BACKEND_BASE_URL",
        "status": "ready",
        "required": true,
        "configured": true,
        "redacted": true,
        "classification": "apply_time_auto_url",
        "resolution_mode": "apply_time_auto",
        "apply_note": "Resolved by write_deploy_local_config.sh during final-apply-resources."
      }
    ]
    """
}

private func blockedFinalResourceRequirementsReport(
    firstBlocker: FinalResourceRequirementsFirstBlocker = FinalResourceRequirementsFirstBlocker(
        id: "MESHY_API_KEY",
        label: "Meshy API key",
        status: "missing",
        classification: "missing_required_value",
        command: "provide MESHY_API_KEY in final-resources.env",
        detail: "Backend-only secret for live Meshy 3D generation.",
        domain: "backend_provider",
        destination: "services/backend/.local/final-resources.env",
        validationCommand: "make final-resources-preflight"
    )
) -> FinalResourceRequirementsReport {
    let meshy = FinalResourceRequirement(
        id: "MESHY_API_KEY",
        label: "Meshy API key",
        domain: "backend_provider",
        destination: "services/backend/.local/final-resources.env",
        sourceTemplate: "MESHY_API_KEY=<secret>",
        required: true,
        secret: true,
        configured: false,
        status: "missing",
        classification: "missing_required_value",
        unblocks: ["game_asset_3d_generation", "provider_key_handoff"],
        validationCommand: "make final-resources-preflight",
        notes: "Backend-only secret for live Meshy 3D generation."
    )
    let openAI = FinalResourceRequirement(
        id: "OPENAI_API_KEY",
        label: "OpenAI API key",
        domain: "backend_provider",
        destination: "services/backend/.local/final-resources.env",
        sourceTemplate: "OPENAI_API_KEY=<secret>",
        required: true,
        secret: true,
        configured: false,
        status: "missing",
        classification: "missing_required_value",
        unblocks: ["npc_agent_runtime"],
        validationCommand: "make final-resources-preflight",
        notes: "Backend-only secret for live NPC agent runtime."
    )
    return FinalResourceRequirementsReport(
        kind: "final_resource_requirements_report",
        status: "blocked",
        summary: FinalResourceRequirementsSummary(
            total: 13,
            ready: 3,
            missing: 5,
            blocked: 0,
            optional: 5,
            required: 5,
            secret: 4,
            backend: 10,
            ios: 4,
            print: 4,
            validationCommands: 4
        ),
        requirements: [meshy, openAI],
        requirementsById: [
            "MESHY_API_KEY": meshy,
            "OPENAI_API_KEY": openAI,
        ],
        firstBlocker: firstBlocker,
        operatorActions: [
            "provide MESHY_API_KEY in final-resources.env",
            "provide OPENAI_API_KEY in final-resources.env",
        ],
        validationCommands: ["make final-resources-preflight"],
        resourcesFile: FinalResourcesFileStatus(
            path: "services/backend/.local/final-resources.env",
            exists: false
        ),
        safety: FinalResourceRequirementsSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            liveProviderCalls: false,
            globalMutation: false
        )
    )
}

private func readyFinalResourceRequirementsReport() -> FinalResourceRequirementsReport {
    let meshy = FinalResourceRequirement(
        id: "MESHY_API_KEY",
        label: "Meshy API key",
        domain: "backend_provider",
        destination: "services/backend/.local/final-resources.env",
        sourceTemplate: "MESHY_API_KEY=<secret>",
        required: true,
        secret: true,
        configured: true,
        status: "ready",
        classification: "configured",
        unblocks: ["game_asset_3d_generation", "provider_key_handoff"],
        validationCommand: "make final-resources-preflight",
        notes: "Backend-only secret for live Meshy 3D generation."
    )
    let backendURL = FinalResourceRequirement(
        id: "PMF_BACKEND_BASE_URL",
        label: "iPhone backend URL",
        domain: "ios_deploy",
        destination: "services/backend/.local/final-resources.env",
        sourceTemplate: "PMF_BACKEND_BASE_URL=auto",
        required: true,
        secret: false,
        configured: true,
        status: "ready",
        classification: "apply_time_auto_url",
        unblocks: ["ios_deployable"],
        validationCommand: "make mobile-deploy-preflight",
        notes: "Auto backend URL is resolved while applying resources.",
        resolutionMode: "apply_time_auto",
        applyNote: "Resolved by write_deploy_local_config.sh during final-apply-resources."
    )
    return FinalResourceRequirementsReport(
        kind: "final_resource_requirements_report",
        status: "ready",
        summary: FinalResourceRequirementsSummary(
            total: 13,
            ready: 13,
            missing: 0,
            blocked: 0,
            optional: 5,
            required: 5,
            secret: 4,
            backend: 10,
            ios: 4,
            print: 4,
            validationCommands: 4
        ),
        requirements: [meshy, backendURL],
        requirementsById: [
            "MESHY_API_KEY": meshy,
            "PMF_BACKEND_BASE_URL": backendURL,
        ],
        firstBlocker: nil,
        operatorActions: ["make final-resource-requirements"],
        validationCommands: ["make final-resources-preflight", "make mobile-deploy-preflight"],
        resourcesFile: FinalResourcesFileStatus(
            path: "services/backend/.local/final-resources.env",
            exists: true
        ),
        safety: FinalResourceRequirementsSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            liveProviderCalls: false,
            globalMutation: false
        )
    )
}

private func blockedFinalResourceFillGuideReport(
    fillAction: String = "fill MESHY_API_KEY in services/backend/.local/final-resources.env",
    firstBlocker: FinalResourceFillGuideFirstBlocker? = nil
) -> FinalResourceFillGuideReport {
    FinalResourceFillGuideReport(
        kind: "final_resource_fill_guide_report",
        status: "blocked",
        summary: FinalResourceFillGuideSummary(
            requiredInputs: 5,
            optionalInputs: 5,
            configuredInputs: 3,
            secretInputs: 4
        ),
        requiredInputs: [
            FinalResourceFillGuideItem(
                id: "MESHY_API_KEY",
                label: "Meshy API key",
                domain: "backend_provider",
                status: "missing",
                classification: "missing_required_value",
                required: true,
                secret: true,
                displayValue: "<secret: fill locally>",
                inputSource: "services/backend/.local/final-resources.env",
                writeDestination: "services/backend/.env",
                applyCommand: "make final-apply-resources",
                validationCommand: "make final-resources-preflight",
                fillAction: fillAction,
                notes: "Backend-only secret for live Meshy 3D generation.",
                unblocks: ["game_asset_3d_generation", "provider_key_handoff"]
            )
        ],
        firstBlocker: firstBlocker,
        commands: ["make final-resource-requirements"],
        safety: FinalResourceFillGuideSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            writesFinalResources: false,
            liveProviderCalls: false,
            globalMutation: false
        )
    )
}

private func readyFinalResourceFillGuideReport() -> FinalResourceFillGuideReport {
    FinalResourceFillGuideReport(
        kind: "final_resource_fill_guide_report",
        status: "ready",
        summary: FinalResourceFillGuideSummary(
            requiredInputs: 2,
            optionalInputs: 0,
            configuredInputs: 2,
            secretInputs: 1
        ),
        requiredInputs: [
            FinalResourceFillGuideItem(
                id: "MESHY_API_KEY",
                label: "Meshy API key",
                domain: "backend_provider",
                status: "ready",
                classification: "configured",
                required: true,
                secret: true,
                displayValue: "<secret: configured>",
                inputSource: "services/backend/.local/final-resources.env",
                writeDestination: "services/backend/.env",
                applyCommand: "make final-apply-resources",
                validationCommand: "make final-resources-preflight",
                fillAction: "review MESHY_API_KEY in final resources",
                notes: "Backend-only secret for live Meshy 3D generation.",
                unblocks: ["game_asset_3d_generation"]
            )
        ],
        configuredInputs: [
            FinalResourceFillGuideItem(
                id: "PMF_BACKEND_BASE_URL",
                label: "iPhone backend URL",
                domain: "ios_deploy",
                status: "ready",
                classification: "configured",
                required: true,
                secret: false,
                displayValue: "http://192.168.1.10:8080",
                inputSource: "apps/mobile/ios/Config/Deployment.local.xcconfig",
                writeDestination: "apps/mobile/ios/Config/Deployment.local.xcconfig",
                applyCommand: "make final-apply-resources",
                validationCommand: "make mobile-deploy-preflight",
                fillAction: "review PMF_BACKEND_BASE_URL before launch",
                notes: "iPhone-reachable LAN URL.",
                unblocks: ["ios_deployable"]
            )
        ],
        commands: ["make final-resource-requirements"],
        safety: FinalResourceFillGuideSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            writesFinalResources: false,
            liveProviderCalls: false,
            globalMutation: false
        )
    )
}

private func blockedFinalResourceApplyPreviewReport(
    firstBlocker: FinalResourceApplyPreviewFirstBlocker = FinalResourceApplyPreviewFirstBlocker(
        id: "backend_env",
        label: "Backend env",
        status: "missing",
        classification: "missing_required_value",
        command: "make final-apply-resources",
        detail: "blocked by MESHY_API_KEY",
        destination: "services/backend/.env",
        writer: "services/backend/scripts/write_backend_env.sh",
        blockedBy: ["MESHY_API_KEY"],
        validationCommand: "make final-resources-preflight"
    )
) -> FinalResourceApplyPreviewReport {
    let backendTarget = FinalResourceApplyPreviewTarget(
        id: "backend_env",
        label: "Backend env",
        destination: "services/backend/.env",
        writer: "services/backend/scripts/write_backend_env.sh",
        status: "missing",
        command: "make final-apply-resources",
        slots: [
            FinalResourceApplyPreviewSlot(
                id: "MESHY_API_KEY",
                status: "missing",
                required: true,
                secret: true,
                configured: false,
                classification: "missing_required_value",
                redacted: true,
                writes: ["MESHY_API_KEY"]
            )
        ],
        blockedBy: ["MESHY_API_KEY"],
        notes: ["Preview does not write services/backend/.env."]
    )
    let iosTarget = FinalResourceApplyPreviewTarget(
        id: "ios_deploy_config",
        label: "iOS deploy config",
        destination: "apps/mobile/ios/Config/Deployment.local.xcconfig",
        writer: "apps/mobile/ios/scripts/write_deploy_local_config.sh",
        status: "missing",
        command: "make final-apply-resources",
        slots: [
            FinalResourceApplyPreviewSlot(
                id: "PMF_BACKEND_BASE_URL",
                status: "missing",
                required: true,
                secret: false,
                configured: false,
                classification: "missing_required_value",
                redacted: false,
                writes: ["PMF_BACKEND_BASE_URL"]
            )
        ],
        blockedBy: ["PMF_BACKEND_BASE_URL"],
        notes: ["Preview does not write Deployment.local.xcconfig."]
    )
    return FinalResourceApplyPreviewReport(
        kind: "final_resource_apply_preview_report",
        status: "blocked",
        summary: FinalResourceApplyPreviewSummary(
            ready: 3,
            missing: 5,
            blocked: 0,
            optional: 5,
            secret: 4,
            backend: 9,
            ios: 4,
            print: 4,
            writeTargets: 2
        ),
        resourcesFile: FinalResourcesFileStatus(
            path: "services/backend/.local/final-resources.env",
            exists: true
        ),
        writeTargets: [backendTarget, iosTarget],
        writeTargetsById: [
            "backend_env": backendTarget,
            "ios_deploy_config": iosTarget,
        ],
        firstBlocker: firstBlocker,
        operatorActions: ["make final-apply-resources"],
        commands: [
            "make final-resource-apply-preview",
            "make final-resources-preflight",
            "make final-apply-resources",
        ],
        safety: FinalResourceApplyPreviewSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            runsShellWriters: false,
            liveProviderCalls: false,
            globalMutation: false,
            xcodeOrSigning: false
        )
    )
}

private func readyFinalResourceApplyPreviewReport() -> FinalResourceApplyPreviewReport {
    let backendTarget = FinalResourceApplyPreviewTarget(
        id: "backend_env",
        label: "Backend env",
        destination: "services/backend/.env",
        writer: "services/backend/scripts/write_backend_env.sh",
        status: "ready",
        command: "make final-apply-resources",
        slots: [
            FinalResourceApplyPreviewSlot(
                id: "MESHY_API_KEY",
                status: "ready",
                required: true,
                secret: true,
                configured: true,
                classification: "configured",
                redacted: true,
                writes: ["MESHY_API_KEY"]
            )
        ],
        notes: ["Preview does not write services/backend/.env."]
    )
    let iosTarget = FinalResourceApplyPreviewTarget(
        id: "ios_deploy_config",
        label: "iOS deploy config",
        destination: "apps/mobile/ios/Config/Deployment.local.xcconfig",
        writer: "apps/mobile/ios/scripts/write_deploy_local_config.sh",
        status: "ready",
        command: "make final-apply-resources",
        slots: [
            FinalResourceApplyPreviewSlot(
                id: "PMF_BACKEND_BASE_URL",
                status: "ready",
                required: true,
                secret: false,
                configured: true,
                classification: "apply_time_auto_url",
                redacted: true,
                writes: ["PMF_BACKEND_BASE_URL"],
                resolutionMode: "apply_time_auto",
                applyNote: "Resolved by write_deploy_local_config.sh during final-apply-resources."
            )
        ],
        notes: ["Preview does not write Deployment.local.xcconfig."]
    )
    return FinalResourceApplyPreviewReport(
        kind: "final_resource_apply_preview_report",
        status: "ready",
        summary: FinalResourceApplyPreviewSummary(
            ready: 8,
            missing: 0,
            blocked: 0,
            optional: 5,
            secret: 4,
            backend: 9,
            ios: 4,
            print: 4,
            writeTargets: 2
        ),
        resourcesFile: FinalResourcesFileStatus(
            path: "services/backend/.local/final-resources.env",
            exists: true
        ),
        writeTargets: [backendTarget, iosTarget],
        writeTargetsById: [
            "backend_env": backendTarget,
            "ios_deploy_config": iosTarget,
        ],
        firstBlocker: nil,
        operatorActions: [],
        commands: [
            "make final-resource-apply-preview",
            "make final-resources-preflight",
            "make final-apply-resources",
        ],
        safety: FinalResourceApplyPreviewSafety(
            providerSecretsInReport: false,
            localPathsInReport: false,
            writesBackendEnv: false,
            writesIosDeployConfig: false,
            runsShellWriters: false,
            liveProviderCalls: false,
            globalMutation: false,
            xcodeOrSigning: false
        )
    )
}

private func defaultFinalDemoLaunchCommands(mode: String) -> [String] {
    if mode.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "configured" {
        return configuredFinalDemoLaunchCommands()
    }
    return ["make backend-device-demo"]
}

private func configuredFinalDemoLaunchCommands() -> [String] {
    [
        "make final-resource-requirements",
        "make final-resources-preflight",
        "make final-resource-apply-preview",
        "make final-apply-resources",
        "make visual-regression-local",
        "make live-provider-evidence",
        "make ios-deploy-runbook",
        "make ios-device-launch-rehearsal",
        "make backend-device-demo",
        "make provider-handoff",
        "make final-demo-launch-configured",
        "make final-acceptance-local",
        "make final-acceptance-configured",
        "make mobile-deploy-preflight",
        "make mobile-xcode-build",
    ]
}

private func finalDemoLaunchReport(
    mode: String = "local",
    includeStatus: Bool = true,
    status: String? = nil,
    overallStatus: String = "partial",
    firstBlockerJSON: String = "null",
    nextActionJSON: String = "null",
    unsafeDetail: String = "Launch report partial; review operator checklist.",
    commands: [String]? = nil,
    finalResourcesStatus: String = "ready",
    finalResourcesAction: String = "run make final-resource-init",
    finalResourcesItemsJSON: String = "[]",
    finalAcceptanceStatus: String = "missing",
    finalAcceptanceFreshnessStatus: String = "fresh",
    finalAcceptanceFreshnessClassification: String = "fresh_report",
    finalAcceptanceBlockerDetail: String = "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.",
    threeDEvaluationStatus: String = "missing",
    threeDEvaluationBlockerClassification: String = "three_d_evaluation_failed",
    threeDEvaluationBlockerDetail: String = "3D evaluation report contains failed cases.",
    visualRegressionStatus: String = "missing",
    visualRegressionFreshnessStatus: String = "fresh",
    visualRegressionFreshnessClassification: String = "fresh_report",
    visualRegressionBlockerClassification: String = "visual_regression_failed",
    visualRegressionBlockerDetail: String = "Visual regression report contains failed artifacts.",
    visualRegressionAction: String = "run make visual-regression-local",
    localShowcaseSmokeStatus: String = "succeeded",
    localShowcaseSmokeFailureDetail: String = "Local HTTP smoke completed.",
    liveProviderEvidenceStatus: String = "missing",
    liveProviderEvidenceBlockerDetail: String = "Missing provider handoff.",
    liveProviderEvidenceFirstID: String? = nil,
    liveProviderEvidenceFirstLabel: String? = nil,
    liveProviderEvidenceFirstStatus: String? = nil,
    liveProviderEvidenceFirstClassification: String? = nil,
    liveProviderEvidenceCommand: String? = nil,
    configuredEvidencePlanStatus: String = "blocked",
    configuredEvidencePlanBlockerDetail: String = "Configured 3D evidence requires MESHY_API_KEY and live provider consent.",
    configuredEvidenceBundleStatus: String = "blocked",
    configuredEvidenceBundleBlockerDetail: String = "Final resource fill guide is blocked before configured evidence bundle.",
    printFulfillmentReadinessStatus: String = "partial",
    printFulfillmentReadinessBlockerDetail: String = "Local print proof is ready; configured Treatstock quote evidence is not present.",
    printFulfillmentReadinessAction: String = "make print-fulfillment-readiness",
    finalResourceApplyPreviewStatus: String = "missing",
    finalShowcaseReadinessStatus: String = "partial",
    finalShowcaseReadinessFirstBlockerDetail: String = "iOS deploy runbook and device launch rehearsal must both be ready.",
    finalShowcaseReadinessAction: String = "make ios-device-launch-rehearsal",
    finalShowcaseReadinessActions: [String]? = nil,
    npcEvaluationStatus: String = "missing",
    npcEvaluationBlockerClassification: String = "npc_agent_evaluation_failed",
    npcEvaluationBlockerDetail: String = "NPC Agent evaluation report contains failed cases.",
    finalOperatorHandoffStatus: String = "missing",
    finalOperatorHandoffAction: String = "run make final-acceptance-local to write services/backend/.local/final-acceptance-local.json",
    iosDeployRunbookStatus: String = "partial",
    iosDeployRunbookSlotStatus: String = "ready",
    iosDeployRunbookThreeDSlotStatus: String = "ready",
    iosDeployRunbookAction: String = "set PMF_BACKEND_BASE_URL to the Mac LAN URL",
    iosDeployRunbookCommand: String = "make mobile-deploy-preflight",
    iosDeviceEvidenceStatus: String = "blocked",
    iosDeviceEvidenceSlotStatus: String = "missing",
    iosDeviceEvidenceAction: String = "run make mobile-deploy-preflight after backend is running",
    iosDeviceEvidenceDetail: String = "Run mobile deploy preflight after backend-device-demo is reachable.",
    iosDeviceEvidenceCommand: String = "make mobile-deploy-preflight",
    iosDeviceLaunchRehearsalStatus: String = "missing",
    iosDeviceLaunchRehearsalAction: String = "run make ios-device-launch-rehearsal",
    iosDeviceLaunchRehearsalActions: [String]? = nil,
    iosDeviceLaunchRehearsalCommand: String = "make final-handoff-index",
    iosDeviceLaunchRehearsalDetail: String = "Final handoff index is stale; rerun safe refresh.",
    iosDeviceLaunchRehearsalFreshnessStatus: String = "fresh",
    iosDeviceLaunchRehearsalFreshnessClassification: String = "fresh_report",
    iosDeviceLaunchRehearsalFreshnessSourceModifiedAt: String = "2026-06-07T12:05:00Z",
    iosDeviceLaunchRehearsalFreshnessCurrentRevision: String = "abc1234",
    iosDeviceLaunchSourceFreshnessStatus: String = "fresh",
    iosDeviceLaunchSourceFreshnessClassification: String = "fresh_report",
    iosDeviceLaunchSourceFreshnessSummaryJSON: String = #"{"fresh": 1, "stale": 0, "unknown": 0}"#,
    iosDeviceLaunchCertificateStatus: String = "blocked",
    iosDeviceLaunchCertificateGateStatus: String = "blocked",
    iosDeviceLaunchCertificateAction: String = "run make final-handoff-index",
    resourceHandoffStatus: String = "blocked",
    resourceHandoffBackendStatus: String = "missing",
    resourceHandoffIOSStatus: String = "blocked",
    resourceHandoffAction: String = "provide MESHY_API_KEY",
    resourceHandoffDestination: String = "services/backend/.env",
    externalActionLedgerCommand: String = "make final-external-action-ledger",
    externalActionLedgerDetail: String = "Inspect external action blockers.",
    closurePacketActionCommand: String = "make final-resource-fill-guide",
    closurePacketActionDetail: String = "Backend-only secret for live Meshy 3D generation.",
    closurePacketFirstBlockerCommand: String = "make final-resources-preflight",
    closurePacketFirstBlockerDetail: String = "Backend-only secret for live Meshy 3D generation.",
    closurePacketConfiguredBundleStatus: String = "blocked",
    closurePacketConfiguredBundleCommand: String = "make configured-live-evidence-bundle",
    closurePacketConfiguredBundleDetail: String = "Build configured live evidence bundle after resource and provider evidence are ready."
) -> FinalDemoLaunchReport {
    try! PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            mode: mode,
            includeStatus: includeStatus,
            status: status,
            overallStatus: overallStatus,
            firstBlockerJSON: firstBlockerJSON,
            nextActionJSON: nextActionJSON,
            unsafeDetail: unsafeDetail,
            commands: commands,
            finalResourcesStatus: finalResourcesStatus,
            finalResourcesAction: finalResourcesAction,
            finalResourcesItemsJSON: finalResourcesItemsJSON,
            finalAcceptanceStatus: finalAcceptanceStatus,
            finalAcceptanceFreshnessStatus: finalAcceptanceFreshnessStatus,
            finalAcceptanceFreshnessClassification: finalAcceptanceFreshnessClassification,
            finalAcceptanceBlockerDetail: finalAcceptanceBlockerDetail,
            threeDEvaluationStatus: threeDEvaluationStatus,
            threeDEvaluationBlockerClassification: threeDEvaluationBlockerClassification,
            threeDEvaluationBlockerDetail: threeDEvaluationBlockerDetail,
            visualRegressionStatus: visualRegressionStatus,
            visualRegressionFreshnessStatus: visualRegressionFreshnessStatus,
            visualRegressionFreshnessClassification: visualRegressionFreshnessClassification,
            visualRegressionBlockerClassification: visualRegressionBlockerClassification,
            visualRegressionBlockerDetail: visualRegressionBlockerDetail,
            visualRegressionAction: visualRegressionAction,
            localShowcaseSmokeStatus: localShowcaseSmokeStatus,
            localShowcaseSmokeFailureDetail: localShowcaseSmokeFailureDetail,
            liveProviderEvidenceStatus: liveProviderEvidenceStatus,
            liveProviderEvidenceBlockerDetail: liveProviderEvidenceBlockerDetail,
            liveProviderEvidenceFirstID: liveProviderEvidenceFirstID,
            liveProviderEvidenceFirstLabel: liveProviderEvidenceFirstLabel,
            liveProviderEvidenceFirstStatus: liveProviderEvidenceFirstStatus,
            liveProviderEvidenceFirstClassification: liveProviderEvidenceFirstClassification,
            liveProviderEvidenceCommand: liveProviderEvidenceCommand,
            configuredEvidencePlanStatus: configuredEvidencePlanStatus,
            configuredEvidencePlanBlockerDetail: configuredEvidencePlanBlockerDetail,
            configuredEvidenceBundleStatus: configuredEvidenceBundleStatus,
            configuredEvidenceBundleBlockerDetail: configuredEvidenceBundleBlockerDetail,
            printFulfillmentReadinessStatus: printFulfillmentReadinessStatus,
            printFulfillmentReadinessBlockerDetail: printFulfillmentReadinessBlockerDetail,
            printFulfillmentReadinessAction: printFulfillmentReadinessAction,
            finalResourceApplyPreviewStatus: finalResourceApplyPreviewStatus,
            finalShowcaseReadinessStatus: finalShowcaseReadinessStatus,
            finalShowcaseReadinessFirstBlockerDetail: finalShowcaseReadinessFirstBlockerDetail,
            finalShowcaseReadinessAction: finalShowcaseReadinessAction,
            finalShowcaseReadinessActions: finalShowcaseReadinessActions,
            npcEvaluationStatus: npcEvaluationStatus,
            npcEvaluationBlockerClassification: npcEvaluationBlockerClassification,
            npcEvaluationBlockerDetail: npcEvaluationBlockerDetail,
            finalOperatorHandoffStatus: finalOperatorHandoffStatus,
            finalOperatorHandoffAction: finalOperatorHandoffAction,
            iosDeployRunbookStatus: iosDeployRunbookStatus,
            iosDeployRunbookSlotStatus: iosDeployRunbookSlotStatus,
            iosDeployRunbookThreeDSlotStatus: iosDeployRunbookThreeDSlotStatus,
            iosDeployRunbookAction: iosDeployRunbookAction,
            iosDeployRunbookCommand: iosDeployRunbookCommand,
            iosDeviceEvidenceStatus: iosDeviceEvidenceStatus,
            iosDeviceEvidenceSlotStatus: iosDeviceEvidenceSlotStatus,
            iosDeviceEvidenceAction: iosDeviceEvidenceAction,
            iosDeviceEvidenceDetail: iosDeviceEvidenceDetail,
            iosDeviceEvidenceCommand: iosDeviceEvidenceCommand,
            iosDeviceLaunchRehearsalStatus: iosDeviceLaunchRehearsalStatus,
            iosDeviceLaunchRehearsalAction: iosDeviceLaunchRehearsalAction,
            iosDeviceLaunchRehearsalActions: iosDeviceLaunchRehearsalActions,
            iosDeviceLaunchRehearsalCommand: iosDeviceLaunchRehearsalCommand,
            iosDeviceLaunchRehearsalDetail: iosDeviceLaunchRehearsalDetail,
            iosDeviceLaunchRehearsalFreshnessStatus: iosDeviceLaunchRehearsalFreshnessStatus,
            iosDeviceLaunchRehearsalFreshnessClassification: iosDeviceLaunchRehearsalFreshnessClassification,
            iosDeviceLaunchRehearsalFreshnessSourceModifiedAt: iosDeviceLaunchRehearsalFreshnessSourceModifiedAt,
            iosDeviceLaunchRehearsalFreshnessCurrentRevision: iosDeviceLaunchRehearsalFreshnessCurrentRevision,
            iosDeviceLaunchSourceFreshnessStatus: iosDeviceLaunchSourceFreshnessStatus,
            iosDeviceLaunchSourceFreshnessClassification: iosDeviceLaunchSourceFreshnessClassification,
            iosDeviceLaunchSourceFreshnessSummaryJSON: iosDeviceLaunchSourceFreshnessSummaryJSON,
            iosDeviceLaunchCertificateStatus: iosDeviceLaunchCertificateStatus,
            iosDeviceLaunchCertificateGateStatus: iosDeviceLaunchCertificateGateStatus,
            iosDeviceLaunchCertificateAction: iosDeviceLaunchCertificateAction,
            resourceHandoffStatus: resourceHandoffStatus,
            resourceHandoffBackendStatus: resourceHandoffBackendStatus,
            resourceHandoffIOSStatus: resourceHandoffIOSStatus,
            resourceHandoffAction: resourceHandoffAction,
            resourceHandoffDestination: resourceHandoffDestination,
            externalActionLedgerCommand: externalActionLedgerCommand,
            externalActionLedgerDetail: externalActionLedgerDetail,
            closurePacketActionCommand: closurePacketActionCommand,
            closurePacketActionDetail: closurePacketActionDetail,
            closurePacketFirstBlockerCommand: closurePacketFirstBlockerCommand,
            closurePacketFirstBlockerDetail: closurePacketFirstBlockerDetail,
            closurePacketConfiguredBundleStatus: closurePacketConfiguredBundleStatus,
            closurePacketConfiguredBundleCommand: closurePacketConfiguredBundleCommand,
            closurePacketConfiguredBundleDetail: closurePacketConfiguredBundleDetail
        )
    )
}

private func demoScript(
    captureSelection: CaptureMediaSelection? = readyGuidedScanSelection(),
    session: MythSession? = nil,
    npcTickHistoryCount: Int = 0,
    printQuote: PrintQuote? = nil,
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil,
    finalLaunchSummary: FinalLaunchMobileSummary? = nil
) -> DemoScript {
    DemoScriptBuilder.build(
        captureSelection: captureSelection,
        session: session,
        npcTickHistoryCount: npcTickHistoryCount,
        printQuote: printQuote,
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError,
        finalLaunchSummary: finalLaunchSummary
    )
}

private func autopilotPlan(
    script: DemoScript,
    phase: ForgeFlowPhase = .idle,
    session: MythSession?,
    npcTickHistoryCount: Int = 0,
    printQuote: PrintQuote? = nil,
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil,
    isAdvancingNPCTick: Bool = false,
    isRunningAutonomy: Bool = false,
    isLoadingPrintQuote: Bool = false
) -> ShowcaseAutopilotPlan {
    ShowcaseAutopilotPlanner.plan(
        script: script,
        phase: phase,
        session: session,
        npcTickHistoryCount: npcTickHistoryCount,
        printQuote: printQuote,
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError,
        isAdvancingNPCTick: isAdvancingNPCTick,
        isRunningAutonomy: isRunningAutonomy,
        isLoadingPrintQuote: isLoadingPrintQuote
    )
}

private func localDemoProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: true,
        overallRealReady: false,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "local",
                status: "local_stub",
                isDemoReady: true,
                isRealProviderReady: false
            ),
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "local",
                status: "local_agent_runtime",
                isDemoReady: true,
                isRealProviderReady: false
            ),
        ]
    )
}

private func realThreeDProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: true,
        overallRealReady: true,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "meshy",
                status: "ready",
                isDemoReady: true,
                isRealProviderReady: true
            ),
        ]
    )
}

private func openAINPCProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: true,
        overallRealReady: true,
        providers: [
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "openai",
                status: "ready",
                isDemoReady: true,
                isRealProviderReady: true,
                capabilities: ["structured_agent_traces", "structured_agent_ticks"]
            ),
        ]
    )
}

private func missingThreeDProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: false,
        overallRealReady: false,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "meshy",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["MESHY_API_KEY"]
            ),
        ]
    )
}

private func missingOpenAINPCProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: false,
        overallRealReady: false,
        providers: [
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "openai",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["OPENAI_API_KEY"]
            ),
        ]
    )
}

private func missingProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: false,
        overallRealReady: false,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "meshy",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["MESHY_API_KEY"]
            ),
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "openai",
                status: "missing_configuration",
                isDemoReady: false,
                isRealProviderReady: false,
                missingEnv: ["OPENAI_API_KEY"]
            ),
        ]
    )
}

private func readyConfiguredProviderReadiness() -> ProviderReadinessResponse {
    ProviderReadinessResponse(
        overallDemoReady: true,
        overallRealReady: true,
        providers: [
            ProviderReadinessItem(
                kind: "three_d",
                selectedProvider: "meshy",
                status: "ready",
                isDemoReady: true,
                isRealProviderReady: true,
                capabilities: ["text_to_3d", "image_to_3d", "multi_image_to_3d"]
            ),
            ProviderReadinessItem(
                kind: "npc",
                selectedProvider: "openai",
                status: "ready",
                isDemoReady: true,
                isRealProviderReady: true,
                capabilities: ["structured_agent_traces", "structured_agent_ticks"]
            ),
            ProviderReadinessItem(
                kind: "print",
                selectedProvider: "treatstock",
                status: "ready",
                isDemoReady: true,
                isRealProviderReady: true,
                capabilities: ["quote", "order_handoff"]
            ),
        ]
    )
}

private func captureMedia(
    filename: String,
    contentType: String,
    kind: CaptureMediaKind,
    data: Data = Data("capture-data".utf8)
) -> CaptureMediaDraft {
    CaptureMediaDraft(
        originalFilename: filename,
        contentType: contentType,
        data: data,
        kind: kind
    )
}

private func guidedScanImage(
    filename: String,
    contentType: String,
    data: Data = Data("scan-image".utf8)
) -> GuidedScanImageFile {
    GuidedScanImageFile(
        filename: filename,
        contentType: contentType,
        data: data
    )
}

private func generatedAsset(
    format: String,
    uri: String,
    variants: [GeneratedAssetVariant] = []
) -> GeneratedAsset {
    GeneratedAsset(
        kind: "game_asset",
        provider: "meshy",
        format: format,
        uri: uri,
        prompt: "a brass key relic",
        moderationStatus: "approved",
        variants: variants
    )
}

private func preparedArtifactAsset(
    asset: GeneratedAsset,
    status: PreparedArtifactAssetStatus,
    cachedURL: URL?,
    sceneURL: URL?,
    statusTitle: String,
    statusDetail: String
) -> PreparedArtifactAsset {
    PreparedArtifactAsset(
        preview: ArtifactPreviewState(asset: asset, title: "The Key That Remembered"),
        sourceURI: asset.uri,
        cachedURL: cachedURL,
        sceneURL: sceneURL,
        status: status,
        statusTitle: statusTitle,
        statusDetail: statusDetail
    )
}

private func sampleNPCAgentTrace(npcId: String) -> NPCAgentTrace {
    NPCAgentTrace(
        npcId: npcId,
        name: npcId.capitalized,
        belief: "The relic changes the village.",
        intention: "interpret the relic",
        proposedAction: "circle the artifact",
        rationale: "It is newly sacred.",
        confidence: 0.82
    )
}

private func mythSession(asset: GeneratedAsset) -> MythSession {
    MythSession(
        sessionId: "myth_test",
        status: "ready",
        objectCard: ObjectCard(
            label: "old brass key",
            materials: ["brass"],
            source: "phone_capture",
            affordances: ["opens"],
            symbolicReading: "memory"
        ),
        mythSeed: MythSeed(
            title: "The Key That Remembered",
            personalResonance: "It holds a small deadline in its teeth.",
            generationPrompt: "a brass key relic"
        ),
        generatedAsset: asset,
        npcDirector: "local",
        npcReactions: [],
        worldResolution: WorldResolution(
            arbitrator: "local",
            summary: "The village gathers.",
            acceptedActions: [],
            rejectedActions: [],
            worldStateDelta: [:],
            visibleChanges: []
        ),
        printCandidate: PrintCandidate(
            kind: "print_asset",
            sourceAssetUri: asset.uri,
            provider: "local",
            format: "stl",
            uri: "local://print.stl",
            requiresUserApproval: true,
            approvalReason: "review",
            printabilityNotes: []
        )
    )
}

private func npcTick(sessionId: String, tickIndex: Int) -> NPCAgentTick {
    NPCAgentTick(
        sessionId: sessionId,
        tickIndex: tickIndex,
        agentRuntime: "local_tick_runtime",
        npcAgentTraces: [
            NPCAgentTrace(
                npcId: "mara",
                name: "Mara",
                belief: "The relic remembers prior runs.",
                intention: "Keep the ritual continuous.",
                proposedAction: "move closer to the relic",
                rationale: "A restored village should not feel reset.",
                confidence: 0.82
            )
        ],
        npcReactions: [],
        worldResolution: WorldResolution(
            arbitrator: "local_world_arbitrator",
            summary: "The village preserves continuity.",
            acceptedActions: [
                ResolvedNPCAction(
                    npcId: "mara",
                    action: "move closer to the relic",
                    status: "accepted",
                    reason: "Safe visible action"
                )
            ],
            rejectedActions: [],
            worldStateDelta: ["tick_index": .int(tickIndex)],
            visibleChanges: ["Mara marks restored tick \(tickIndex)."]
        )
    )
}

private func ritualTick(
    sessionId: String,
    tickIndex: Int,
    unsafeSuffix: String = ""
) -> NPCAgentTick {
    NPCAgentTick(
        sessionId: sessionId,
        tickIndex: tickIndex,
        agentRuntime: "local_tick_runtime",
        npcAgentTraces: [
            NPCAgentTrace(
                npcId: "mara",
                name: "Mara",
                belief: "The relic is becoming public\(unsafeSuffix)",
                intention: "invite neighbors",
                proposedAction: "invite neighbors to witness\(unsafeSuffix)",
                rationale: "A public relic needs witnesses.",
                confidence: 0.82
            ),
            NPCAgentTrace(
                npcId: "ior",
                name: "Ior",
                belief: "The relic needs doubt.",
                intention: "slow the ritual",
                proposedAction: "argue about the relic",
                rationale: "A useful village needs friction.",
                confidence: 0.72
            ),
            NPCAgentTrace(
                npcId: "senn",
                name: "Senn",
                belief: "The relic can be named later.",
                intention: "watch the others",
                proposedAction: "watch the ritual",
                rationale: "Observation can become play.",
                confidence: 0.66
            ),
        ],
        npcReactions: [
            NPCReaction(
                npcId: "mara",
                name: "Mara",
                emotion: "awe",
                interpretation: "The relic asks to be witnessed.",
                plan: ["invite neighbors to witness\(unsafeSuffix)"],
                worldChange: "neighbors gather"
            ),
            NPCReaction(
                npcId: "ior",
                name: "Ior",
                emotion: "doubt",
                interpretation: "The relic asks too much.",
                plan: ["argue about the relic"],
                worldChange: "debate rises"
            ),
            NPCReaction(
                npcId: "senn",
                name: "Senn",
                emotion: "wonder",
                interpretation: "The relic feels like a game.",
                plan: ["watch the ritual"],
                worldChange: "children wait"
            ),
        ],
        worldResolution: WorldResolution(
            arbitrator: "local_world_arbitrator",
            summary: "The ritual shifts around the relic.",
            acceptedActions: [
                ResolvedNPCAction(
                    npcId: "mara",
                    action: "invite neighbors to witness\(unsafeSuffix)",
                    status: "accepted",
                    reason: "Safe visible action"
                )
            ],
            rejectedActions: [
                ResolvedNPCAction(
                    npcId: "ior",
                    action: "argue about the relic",
                    status: "rejected",
                    reason: "Too much doubt for this tick"
                )
            ],
            worldStateDelta: ["tick_index": .int(tickIndex)],
            visibleChanges: ["Mara steps forward\(unsafeSuffix).", "Ior circles wide."]
        )
    )
}

private func backendHistorySession() throws -> MythSession {
    var session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    session.sessionId = "myth_0123456789abcdef"
    return session
}

private enum FixtureLoader {
    static func data(from name: String) throws -> Data {
        guard let url = Bundle.module.url(forResource: name, withExtension: "json") else {
            throw ContractTestError.fixtureMissing(name)
        }
        return try Data(contentsOf: url)
    }

    static func decode<T: Decodable>(_ type: T.Type, from name: String) throws -> T {
        return try PMFJSON.decoder.decode(T.self, from: data(from: name))
    }
}

private final class RecordingTransport: HTTPTransport, @unchecked Sendable {
    private(set) var requests: [URLRequest] = []
    private var responses: [HTTPResponse]

    init(responses: [HTTPResponse]) {
        self.responses = responses
    }

    func send(_ request: URLRequest) async throws -> HTTPResponse {
        requests.append(request)
        if responses.isEmpty {
            throw ContractTestError.expectationFailed("No fake response queued")
        }
        return responses.removeFirst()
    }
}

private final class FakeForgeFlowAPI: ForgeFlowAPI, @unchecked Sendable {
    private let uploadResult: Result<ObjectCapture, Error>
    private let sessionResult: Result<MythSession, Error>
    private(set) var uploadedMetadata: ObjectCaptureMetadata?
    private(set) var uploadedMedia: [CaptureUpload] = []
    private(set) var sessionCaptureIds: [String] = []
    private(set) var sessionContexts: [ContextCapsule] = []

    init(uploadResult: Result<ObjectCapture, Error>, sessionResult: Result<MythSession, Error>) {
        self.uploadResult = uploadResult
        self.sessionResult = sessionResult
    }

    func uploadObjectCapture(metadata: ObjectCaptureMetadata, media: [CaptureUpload]) async throws -> ObjectCapture {
        uploadedMetadata = metadata
        uploadedMedia = media
        return try uploadResult.get()
    }

    func createMythSessionFromCapture(captureId: String, context: ContextCapsule) async throws -> MythSession {
        sessionCaptureIds.append(captureId)
        sessionContexts.append(context)
        return try sessionResult.get()
    }
}

private actor RecordingArtifactAssetDownloader: ArtifactAssetDownloader {
    private let data: Data
    private let error: Error?
    private var urls: [URL] = []

    init(data: Data = Data("asset-bytes".utf8), error: Error? = nil) {
        self.data = data
        self.error = error
    }

    func download(from url: URL) async throws -> Data {
        urls.append(url)
        if let error {
            throw error
        }
        return data
    }

    func requestedURLs() -> [URL] {
        urls
    }
}

private actor RecordingArtifactAssetCache: ArtifactAssetCache {
    private let rootURL: URL
    private var filenames: [String] = []
    private var dataValues: [Data] = []

    init(rootURL: URL) {
        self.rootURL = rootURL
    }

    func store(data: Data, filename: String) async throws -> URL {
        filenames.append(filename)
        dataValues.append(data)
        return rootURL.appendingPathComponent(filename)
    }

    func storedFilenames() -> [String] {
        filenames
    }

    func storedData() -> [Data] {
        dataValues
    }
}

private final class SnapshotRecorder: @unchecked Sendable {
    private(set) var values: [ForgeFlowState] = []

    func append(_ state: ForgeFlowState) {
        values.append(state)
    }
}

private func expectEqual<T: Equatable>(_ actual: T, _ expected: T) throws {
    if actual != expected {
        throw ContractTestError.expectationFailed("Expected \(expected), got \(actual)")
    }
}

private func expectTrue(_ value: Bool) throws {
    if !value {
        throw ContractTestError.expectationFailed("Expected true")
    }
}

private func expectFalse(_ value: Bool) throws {
    if value {
        throw ContractTestError.expectationFailed("Expected false")
    }
}

private func expectContains(_ haystack: String, _ needle: String) throws {
    if !haystack.contains(needle) {
        throw ContractTestError.expectationFailed("Expected body to contain \(needle)")
    }
}

private func expectNotContains(_ haystack: String, _ needle: String) throws {
    if haystack.contains(needle) {
        throw ContractTestError.expectationFailed("Expected body not to contain \(needle)")
    }
}

private func require<T>(_ value: T?, _ message: String) throws -> T {
    guard let value else {
        throw ContractTestError.expectationFailed(message)
    }
    return value
}

private func expectCaptureDraftError(_ draft: CaptureDraft, _ expected: CaptureDraftValidationError) throws {
    do {
        _ = try draft.validatedUploadPayload()
        throw ContractTestError.expectationFailed("Expected capture draft error \(expected)")
    } catch let error as CaptureDraftValidationError {
        try expectEqual(error, expected)
    }
}

private func expectGuidedScanPhotoSetBuilderError(
    _ images: [GuidedScanImageFile],
    _ expected: GuidedScanPhotoSetBuilderError
) throws {
    do {
        _ = try GuidedScanPhotoSetBuilder.mediaDrafts(from: images)
        throw ContractTestError.expectationFailed("Expected guided scan builder error \(expected)")
    } catch let error as GuidedScanPhotoSetBuilderError {
        try expectEqual(error, expected)
    }
}

private func expectThrows<E: Error & Equatable>(
    _ expected: E,
    _ operation: () throws -> Void
) throws {
    do {
        try operation()
    } catch let error as E {
        try expectEqual(error, expected)
        return
    } catch {
        throw ContractTestError.expectationFailed("Expected \(expected), got \(error)")
    }

    throw ContractTestError.expectationFailed("Expected \(expected), got no error")
}

private func sourceFile(_ name: String, in directory: URL) throws -> String {
    let url = directory.appendingPathComponent(name)
    guard FileManager.default.fileExists(atPath: url.path) else {
        throw ContractTestError.expectationFailed("Missing source file: \(name)")
    }
    return try String(contentsOf: url, encoding: .utf8)
}

private enum ContractTestError: Error, CustomStringConvertible {
    case fixtureMissing(String)
    case expectationFailed(String)

    var description: String {
        switch self {
        case let .fixtureMissing(name):
            return "Fixture missing: \(name).json"
        case let .expectationFailed(message):
            return message
        }
    }
}
