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
    try testDecodesPrintQuotePayload()
    try testFinalShowcaseSummaryWaitsBeforeSession()
    try testFinalShowcaseSummaryReadyForLocalDemo()
    try testFinalShowcaseSummaryMarksPrintQuoteReady()
    try testFinalShowcaseSummaryMarksProviderErrorNeedsAttention()
    try testFinalShowcaseSummaryRedactsUnsafeSourceText()
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
    try testDevicePreflightMapsFinalLaunchPartialToWaiting()
    try testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting()
    try testDevicePreflightMarksReadyFinalResourcesPreflight()
    try testDevicePreflightBlocksAndRedactsFinalResourcesPreflight()
    try testDevicePreflightBlocksAndRedactsFinalLaunchError()
    try testFinalLaunchMobileSummaryWaitsForMissingReport()
    try testFinalLaunchMobileSummaryBuildsPartialOperatorStatus()
    try testFinalLaunchMobileSummaryMarksReadyReport()
    try testFinalLaunchMobileSummaryRedactsUnsafeReportText()
    try testDevicePreflightMarksLocalDemoReady()
    try testDevicePreflightMarksSavedNPCHistoryReady()
    try testDemoScriptStartsWithCapture()
    try testDemoScriptMovesToForgeWhenMediaReady()
    try testDemoScriptMarksLocalDemoLoopReady()
    try testDemoScriptBlocksOnProviderReadinessError()
    try testDemoScriptRedactsUnsafeDetail()
    try testShowcaseAutopilotBlocksUntilCaptureReady()
    try testShowcaseAutopilotPlansForgeWhenCaptureReady()
    try testShowcaseAutopilotPlansBackendAutonomyForReadySession()
    try testShowcaseAutopilotPlansLegacyTickAdvanceForLegacySession()
    try testShowcaseAutopilotPlansPrintQuoteAfterNPCAutonomy()
    try testShowcaseAutopilotCompletesWhenQuoteAndResourcesReady()
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
    try await testGetFinalDemoLaunchBuildsGETRequest()
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
    try testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset()
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
            finalResourcesAction: "copy services/backend/final-resources.env.example"
        )
    )

    try expectEqual(summary.overallStatus, .waiting)
    try expectEqual(summary.item(id: "final_resources")?.status, .waiting)
    try expectContains(summary.item(id: "final_resources")?.detail ?? "", "missing")
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

private func testFinalLaunchMobileSummaryBuildsPartialOperatorStatus() throws {
    let summary = FinalLaunchMobileSummaryBuilder.build(
        report: finalDemoLaunchReport(
            overallStatus: "partial",
            finalResourcesStatus: "missing",
            finalResourcesAction: "copy services/backend/final-resources.env.example"
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
    try expectContains(summary.resourceActions.first ?? "", "copy services/backend/final-resources.env.example")
    try expectContains(summary.commandRows.first ?? "", "make backend-device-demo")
    try expectContains(summary.notes.joined(separator: " "), "read-only")
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

private func finalDemoLaunchPayload(
    overallStatus: String = "partial",
    unsafeDetail: String = "Launch report partial; review operator checklist.",
    finalResourcesStatus: String = "missing",
    finalResourcesAction: String = "copy services/backend/final-resources.env.example"
) -> Data {
    Data(
        """
        {
          "kind": "final_demo_launch_report",
          "mode": "local",
          "overall_status": "\(overallStatus)",
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
            "items": [],
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
          "commands": ["make backend-device-demo"],
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
    finalDemoLaunch: FinalDemoLaunchReport? = finalDemoLaunchReport(overallStatus: "ready"),
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

private func finalDemoLaunchReport(
    overallStatus: String = "partial",
    unsafeDetail: String = "Launch report partial; review operator checklist.",
    finalResourcesStatus: String = "ready",
    finalResourcesAction: String = "copy services/backend/final-resources.env.example"
) -> FinalDemoLaunchReport {
    try! PMFJSON.decoder.decode(
        FinalDemoLaunchReport.self,
        from: finalDemoLaunchPayload(
            overallStatus: overallStatus,
            unsafeDetail: unsafeDetail,
            finalResourcesStatus: finalResourcesStatus,
            finalResourcesAction: finalResourcesAction
        )
    )
}

private func demoScript(
    captureSelection: CaptureMediaSelection? = readyGuidedScanSelection(),
    session: MythSession? = nil,
    npcTickHistoryCount: Int = 0,
    printQuote: PrintQuote? = nil,
    providerReadiness: ProviderReadinessResponse? = localDemoProviderReadiness(),
    providerReadinessError: String? = nil
) -> DemoScript {
    DemoScriptBuilder.build(
        captureSelection: captureSelection,
        session: session,
        npcTickHistoryCount: npcTickHistoryCount,
        printQuote: printQuote,
        providerReadiness: providerReadiness,
        providerReadinessError: providerReadinessError
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
