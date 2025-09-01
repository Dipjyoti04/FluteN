"""
Main program for Audio to Sargam Transcription - Mobile Version
"""
# Import mobile app
from main_mobile import main

if __name__ == "__main__":
    main()
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        elif choice == '2':
            try:
                freq = float(input("Enter base frequency for Sa (Hz): "))
                transcriber.sargam_converter.set_base_frequency(freq)
                print(f"✅ Base frequency set to {freq:.2f} Hz")
            except ValueError:
                print("❌ Invalid frequency value!")
        
        elif choice == '3':
            ref_path = input("Enter reference audio file path: ").strip()
            if os.path.exists(ref_path):
                try:
                    transcriber.set_base_frequency_from_audio(ref_path)
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            else:
                print("❌ Reference file not found!")
        
        elif choice == '4':
            if transcriber.last_transcription:
                print("\n" + transcriber.format_transcription_text(transcriber.last_transcription))
            else:
                print("No transcription available. Please transcribe an audio file first.")
        
        elif choice == '5':
            print("Goodbye! 🎵")
            break
        
        else:
            print("❌ Invalid option!")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run interactive mode
        interactive_mode()
    else:
        # Command line arguments provided
        main()
