import SwiftUI
import UIKit
import LiquidPhotos
import LiquidGlass
import Kinetics
import WaterfallGrids

/// Temporary vertical slice used to verify every dependency builds and links
/// before the real gallery is assembled.
struct ProbeView: View {
    @State private var photos: [UIImage] = []
    @State private var selection = 0
    @State private var playing = false
    @State private var target = CGPoint(x: 120, y: 120)
    @State private var current = CGPoint(x: 120, y: 120)
    @State private var spring = KineticsSpring.snappy

    var body: some View {
        ZStack {
            Color(red: 0.043, green: 0.047, blue: 0.055).ignoresSafeArea()

            ScrollView {
                VStack(spacing: 20) {
                    header

                    LazyWaterfallGrid(
                        items: .columns([.init(), .init()]),
                        spacing: 10,
                        data: Array(0..<6),
                        id: \.self
                    ) { index in
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(LinearGradient(
                                colors: [.orange.opacity(0.5), .blue.opacity(0.35)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                            .aspectRatio(index.isMultiple(of: 2) ? 0.78 : 1.25, contentMode: .fit)
                            .overlay {
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .stroke(.white.opacity(0.08), lineWidth: 0.5)
                            }
                    }

                    LiquidPhotos(
                        photos,
                        selection: $selection,
                        isPlaying: $playing,
                        style: LiquidPhotosStyle(
                            transitionDuration: 1.0,
                            holdDuration: 2.0,
                            morph: 0.8,
                            cornerRadius: 28
                        )
                    )
                    .frame(height: 420)

                    Circle()
                        .fill(.white.opacity(0.12))
                        .frame(width: 48, height: 48)
                        .position(current)
                        .frame(height: 200)
                        .kinetics(target: $target, current: $current, spring: $spring)
                        .onTapGesture {
                            target = CGPoint(x: .random(in: 40...320), y: .random(in: 40...160))
                        }
                }
                .padding(20)
            }

            VStack {
                Spacer()
                Text("PROBE")
                    .font(.system(size: 11, weight: .bold))
                    .tracking(3)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 10)
                    .glass(style: .toolbar)
            }
            .padding(.bottom, 30)
        }
        .onAppear {
            if photos.isEmpty {
                photos = ProbeImages.make(count: 5)
            }
        }
    }

    private var header: some View {
        HStack {
            Text("Lumen")
                .font(.system(size: 30, weight: .semibold))
            Spacer()
            Image(systemName: "plus")
                .frame(width: 44, height: 44)
                .glass(style: .button)
        }
    }
}

private enum ProbeImages {
    static func make(count: Int) -> [UIImage] {
        (0..<count).compactMap { index in
            let size = CGSize(width: 1200, height: index.isMultiple(of: 2) ? 1600 : 900)
            let renderer = UIGraphicsImageRenderer(size: size)
            return renderer.image { context in
                let cg = context.cgContext
                let colors = [
                    UIColor(red: 0.10, green: 0.12, blue: 0.18, alpha: 1).cgColor,
                    UIColor(red: 1.0, green: 0.42, blue: 0.29, alpha: 1).cgColor,
                    UIColor(red: 0.29, green: 0.62, blue: 1.0, alpha: 1).cgColor
                ] as CFArray
                let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(),
                                          colors: colors,
                                          locations: [0, 0.55, 1])!
                cg.drawLinearGradient(
                    gradient,
                    start: CGPoint(x: 0, y: 0),
                    end: CGPoint(x: size.width, y: size.height),
                    options: []
                )
                cg.setFillColor(UIColor.black.withAlphaComponent(0.35).cgColor)
                cg.fill(CGRect(x: 0, y: size.height * 0.68, width: size.width, height: size.height * 0.32))
            }
        }
    }
}
