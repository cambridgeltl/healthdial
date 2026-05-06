import logging
from init import pymongo
from gridfs import GridFS
from bson.objectid import ObjectId

class GridFs(object):
    """
    GridFs class
    """
    def __init__(self, collection):
        """
        GridFs init
        :param collection: collection name
        """
        logging.info('GridFs init')
        self.file_db = pymongo.db
        self.collection = collection

    def createCollection(self,collection):
        """
        create collection
        :param collection: collection name
        """
        file_table = self.file_db[collection]
        return file_table

    def insertFile(self,file,**kwargs):
        """
        insert file
        :param file: file
        :param kwargs: kwargs
        :return: ObjectId
        """
        fs = GridFS(self.file_db, self.collection)
        filename = kwargs['filename']
        if fs.exists(filename):
            logging.info('file already exists')
        else:
            ObjectId = fs.put(file, **kwargs)
            logging.info(ObjectId)
            return ObjectId

    def getID(self, filename):
        """
        get file id
        :param filename: filename
        :return: ObjectId
        """
        try:
            fs = GridFS(self.file_db, self.collection)
            ObjectId = fs.find_one({"filename":filename})._id
            return ObjectId
        except Exception as e:
            logging.error(e)
            return None

    def getFile(self,id):
        """
        get file
        :param id: ObjectId
        :return: file
        """
        fs = GridFS(self.file_db, self.collection)
        try:
            fileOut = fs.get(id)
            bitData = fileOut.read()
            return bitData
        except Exception as e:
            logging.error(e)

    def deleteFile(self, id):
        """
        delete file
        :param id: ObjectId
        """
        try:
            fs = GridFS(self.file_db, self.collection)
            fs.delete(id)
        except Exception as e:
            logging.error(e)












