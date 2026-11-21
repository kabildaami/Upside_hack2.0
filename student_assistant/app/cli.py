import argparse,asyncio,uuid
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from services.config import DATABASE_URL
from services.db import require_student
from .graph import build_graph

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--student-id',type=int,required=True)
    parser.add_argument('--thread-id',default=None)
    parser.add_argument('--message',default=None)
    args=parser.parse_args()
    require_student(args.student_id)
    thread=args.thread_id or str(uuid.uuid4())
    print('Thread:',thread)
    async def run():
        async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as saver:
            await saver.setup()
            graph=build_graph(checkpointer=saver)
            async def ask(message):
                result=await graph.ainvoke({'student_id':args.student_id,'thread_id':thread,'message':message},
                    config={'configurable':{'thread_id':f'student:{args.student_id}:{thread}'},'recursion_limit':12})
                print('\nAssistant:',result.get('response'))
                if result.get('quiz_id'): print('Quiz ID:',result['quiz_id'])
            if args.message: await ask(args.message)
            else:
                while True:
                    msg=input('\nStudent > ').strip()
                    if msg.lower() in ('exit','quit'): break
                    await ask(msg)
    import sys
    import asyncio

    if sys.platform == "win32":
        asyncio.run(
            run(),
            loop_factory=asyncio.SelectorEventLoop
        )
    else:
        asyncio.run(run())
    if __name__=='__main__':main()
