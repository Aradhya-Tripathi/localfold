import { useState } from 'react'
import { signalsWebsocket } from './Api'
import { Toaster, toast } from 'sonner'

import Setup from './components/Setup'
import QueuedPredictions from './components/QueuedPredictions'

function App() {
  // Todo: https://www.bugpilot.com/guides/en/building-a-chat-application-with-react-and-django-channels-0120
  // to show changes in the prediction state.
  const [queue, setQueue] = useState({})
  const [isConnected, setIsConnected] = useState(true)
  const [toggleSetup, setToggleSetup] = useState(false)

  window.electron.ipcRenderer.on('closing', () => {
    signalsWebsocket.close(1000) //  closing websocket connection as soon as window is closed!
  })

  signalsWebsocket.onerror = (e) => {
    setIsConnected(false)
  }

  signalsWebsocket.onopen = (e) => {
    toast.success('Connected!')
  }

  signalsWebsocket.onmessage = (e) => {
    var message = JSON.parse(e.data)
    if (message.error != undefined) {
      toast.error(message.error)
      return
    }
    setQueue(message.tasks)
  }

  const querySetup = () => {
    /*
     Handle query setup and trigger prediction
     */
    window.electron.ipcRenderer.send('query-selector')
    window.electron.ipcRenderer.on('query-selector-results', (_, msg) => {
      if (msg.filePath === undefined) return

      signalsWebsocket.send(
        JSON.stringify({
          execute: 'add_task',
          arg: msg.filePath[0]
        })
      )
    })
  }

  return (
    <div className="flex flex-col h-screen w-screen justify-center items-center bg-black">
      {isConnected ? (
        <>
          <header className="text-white font-bold text-2xl mt-5">LocalFold</header>
          {toggleSetup && <Setup toggleSetup={toggleSetup} setToggleSetup={setToggleSetup} />}
          {/* <div className="w-screen flex items-center justify-center">
            <input
              type="text"
              className="mt-10 rounded-l text-center border-b-1 focus:outline-none w-3/6 text-black bg-[#FAF9F6] rounded-lg"
              placeholder="Path to query file"
              value={queryPath}
              onChange={(e) => {
                setQueryPath(e.target.value)
              }}
            />
          </div> */}
          {/* <button
            className="text-white bg-transparent mt-2 mb-2 hover:text-gray-200"
            onClick={enqueuePrediction}
          >
            Queue Prediction
          </button> */}
          <QueuedPredictions queue={queue} />
        </>
      ) : (
        <h1 className="text-center text-3xl font-bold text-red-600">Server offline!</h1>
      )}
      <nav className=" h-10 w-full flex justify-center">
        <button
          className="h-full mr-10 font-bold"
          onClick={() => {
            setToggleSetup(!toggleSetup)
          }}
        >
          Model Setup
        </button>
        <button
          className="h-full font-bold"
          onClick={() => {
            querySetup()
          }}
        >
          Select Query File
        </button>
      </nav>
      <Toaster />
    </div>
  )
}

export default App
