import TableCreator
import AnnotationExtractor
import writer
from threading import Thread
import threading

from ThreadSafeCounter import ThreadSafeCounter

threadLock = threading.Lock()
global_counter = 0


def __create_tables(table_creator: TableCreator, folder):
    """create a one single data package (boxes, masks, image...)"""
    images, prefix = table_creator.load_template()

    images[TableCreator.TABLE], table_boxes = AnnotationExtractor.get_table_annotations(images[TableCreator.TABLE])
    overlay = images[TableCreator.REGULAR].copy()
    images[TableCreator.CELL], boxes = AnnotationExtractor.get_cell_annotations(table_boxes, images[TableCreator.CELL],
                                                                                images[TableCreator.TABLE_LINES],
                                                                                overlay)
    writer.write(images, overlay, boxes, prefix, folder=folder)


def __create_table_loop(table_creator, folder, file_count, counter: ThreadSafeCounter):
    """loop to create files for a single thread"""
    i = 0
    while i < file_count:
        __create_tables(table_creator, folder)
        i += 1
        counter.increment()


def start_loop(table_creator, folder='test', thread_count=3, files_per_thread=10):
    """create the files in a multi thread loop until the limit is reached"""

    writer.make_folders(folder=folder)
    counter = ThreadSafeCounter()

    threads = []

    while thread_count > 0:
        # create and start all threads
        thread = Thread(target=__create_table_loop, args=(table_creator, folder, files_per_thread, counter))
        thread.start()
        threads.append(thread)
        thread_count -= 1

    for t in threads:
        t.join()

    print("DONE!")
