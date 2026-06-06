// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "PersonalMythForgeMobile",
    platforms: [.iOS(.v17), .macOS(.v13)],
    products: [
        .library(name: "PersonalMythForgeMobileCore", targets: ["PersonalMythForgeMobileCore"])
    ],
    targets: [
        .target(name: "PersonalMythForgeMobileCore"),
        .executableTarget(
            name: "PersonalMythForgeMobileCoreContractTests",
            dependencies: ["PersonalMythForgeMobileCore"],
            resources: [.process("Fixtures")]
        ),
        .executableTarget(
            name: "PersonalMythForgeMobileProjectChecks",
            dependencies: []
        ),
        .executableTarget(
            name: "PersonalMythForgeMobileAppCompileCheck",
            dependencies: ["PersonalMythForgeMobileCore"],
            path: "App",
            exclude: ["Info.plist"]
        ),
    ]
)
