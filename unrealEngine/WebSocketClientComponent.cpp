#include "WebSocketClientComponent.h"
#include "WebSocketsModule.h"
#include "Async/Async.h"
#include "map"
#include "ACERuntimeModule.h"

UWebSocketClientComponent::UWebSocketClientComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UWebSocketClientComponent::ConnectToServer(const FString& ServerURL)
{
    // Ensure the module is loaded
    if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
    {
        FModuleManager::Get().LoadModule("WebSockets");
    }

    // Create the WebSocket instance (Protocol is usually "ws" or "wss")
    WebSocket = FWebSocketsModule::Get().CreateWebSocket(ServerURL, TEXT("ws"));

    if (WebSocket.IsValid())
    {
        // Bind delegates
        WebSocket->OnConnected().AddUObject(this, &UWebSocketClientComponent::OnConnected);
        WebSocket->OnConnectionError().AddUObject(this, &UWebSocketClientComponent::OnConnectionError);
        WebSocket->OnClosed().AddUObject(this, &UWebSocketClientComponent::OnClosed);
        WebSocket->OnMessage().AddUObject(this, &UWebSocketClientComponent::OnMessage);
        WebSocket->OnRawMessage().AddUObject(this, &UWebSocketClientComponent::OnRawMessage);

        // Initiate connection
        WebSocket->Connect();
    }
}

void UWebSocketClientComponent::OnConnected(){
    // Route gameplay logic to the game thread to avoid crashes
    AsyncTask(ENamedThreads::GameThread, []()
    {
        UE_LOG(LogTemp, Log, TEXT("WebSocket connected successfully!"));
    });
}

void UWebSocketClientComponent::OnConnectionError(){
    AsyncTask(ENamedThreads::GameThread, []()
    {
        UE_LOG(LogTemp, Log, TEXT("WebSocket connection error!"));
    });
}

void UWebSocketClientComponent::OnClosed(){
    AsyncTask(ENamedThreads::GameThread, []()       
    {
        UE_LOG(LogTemp, Log, TEXT("WebSocket disconnected!"));
    });
}

// Receives JSON emotion parameters
void UWebSocketClientComponent::OnMessage(const map& data){
    AsyncTask(ENamedThreads::GameThread, [this, Message]()){
        // Convert to Audio2FaceEmotion data type
    };
}

// Receives raw audio bytes 
void UWebSocketClientComponent::OnRawMessage(const void& data){
    AsyncTask(ENamedThreads::GameThread, [this, Message]()){
        // Upload audio to Audio2Face
        FACERuntimeModule::Get().AnimateFromAudioSamples()
    };
}


// PCM is uncompressed
// bit depth defines the number of posible amplitude values that can be assigned to an audio file
// 16 bit means can represent 2^16 amplitude values
// the LLM outputs audio tokens not playable sound
// We need an encoder/decoder to convert these in an audio waveform --> use SNAC decoder
// lightweight and fast
// expects 7 tokens per group across 3 layers

// We need to:
// identify special audio tokens
// accumulate enough of them to be sent to snac decoder